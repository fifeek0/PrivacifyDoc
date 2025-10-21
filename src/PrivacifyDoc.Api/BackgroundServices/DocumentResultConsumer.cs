using System;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;
using PrivacifyDoc.Domain.Repositories;
using PrivacifyDoc.Domain.Events;
using PrivacifyDoc.Domain.Enums;
using PrivacifyDoc.Domain.Entities;

namespace PrivacifyDoc.Api.BackgroundServices;

public class DocumentResultConsumer : BackgroundService, IDisposable
{
    private readonly ILogger<DocumentResultConsumer> _logger;
    private readonly IServiceProvider _serviceProvider;
    private readonly IConfiguration _configuration;
    private IConnection? _connection;
    private IModel? _channel;
    private readonly string _queueName = "document.anonymized";

    public DocumentResultConsumer(
        ILogger<DocumentResultConsumer> logger,
        IServiceProvider serviceProvider,
        IConfiguration configuration)
    {
        _logger = logger;
        _serviceProvider = serviceProvider;
        _configuration = configuration;
    }

    public override async Task StartAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("DocumentResultConsumer starting...");
        
        try
        {
            await ConnectToRabbitMQ();
            await base.StartAsync(cancellationToken);
            _logger.LogInformation("DocumentResultConsumer started successfully");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to start DocumentResultConsumer");
            throw;
        }
    }

    private async Task ConnectToRabbitMQ()
    {
        var factory = new ConnectionFactory
        {
            HostName = _configuration["RabbitMQ:Host"] ?? "localhost",
            Port = int.Parse(_configuration["RabbitMQ:Port"] ?? "5672"),
            UserName = _configuration["RabbitMQ:Username"] ?? "guest",
            Password = _configuration["RabbitMQ:Password"] ?? "guest"
        };

        var retryCount = 0;
        const int maxRetries = 5;

        while (retryCount < maxRetries)
        {
            try
            {
                _connection = factory.CreateConnection();
                _channel = _connection.CreateModel();

                // Declare the queue
                _channel.QueueDeclare(
                    queue: _queueName,
                    durable: true,
                    exclusive: false,
                    autoDelete: false,
                    arguments: null);

                _logger.LogInformation("Connected to RabbitMQ and declared queue {QueueName}", _queueName);
                return;
            }
            catch (Exception ex)
            {
                retryCount++;
                _logger.LogWarning(ex, "Failed to connect to RabbitMQ (attempt {Attempt}/{MaxRetries})", retryCount, maxRetries);
                
                if (retryCount >= maxRetries)
                    throw;
                    
                await Task.Delay(TimeSpan.FromSeconds(5));
            }
        }
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        if (_channel == null)
        {
            _logger.LogError("Channel is null, cannot start consuming");
            return;
        }

        var consumer = new AsyncEventingBasicConsumer(_channel);
        consumer.Received += OnMessageReceived;

        _channel.BasicQos(prefetchSize: 0, prefetchCount: 1, global: false);
        _channel.BasicConsume(queue: _queueName, autoAck: false, consumer: consumer);

        _logger.LogInformation("Started consuming messages from queue {QueueName}", _queueName);

        // Keep the service running until cancellation is requested
        try
        {
            await Task.Delay(Timeout.Infinite, stoppingToken);
        }
        catch (OperationCanceledException)
        {
            _logger.LogInformation("DocumentResultConsumer execution cancelled");
        }
    }

    private async Task OnMessageReceived(object sender, BasicDeliverEventArgs eventArgs)
    {
        var correlationId = Guid.NewGuid().ToString();
        _logger.LogInformation("Processing message with correlation ID {CorrelationId}", correlationId);

        try
        {
            var body = eventArgs.Body.ToArray();
            var message = Encoding.UTF8.GetString(body);
            
            _logger.LogDebug("Received message: {Message} | CorrelationId: {CorrelationId}", message, correlationId);

            var anonymizedEvent = JsonSerializer.Deserialize<DocumentAnonymizedEvent>(message, new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase
            });

            if (anonymizedEvent == null)
            {
                _logger.LogError("Failed to deserialize DocumentAnonymizedEvent | CorrelationId: {CorrelationId}", correlationId);
                _channel?.BasicNack(eventArgs.DeliveryTag, false, false); // Don't requeue invalid messages
                return;
            }

            await ProcessDocumentAnonymizedEvent(anonymizedEvent, correlationId);

            // Acknowledge successful processing
            _channel?.BasicAck(eventArgs.DeliveryTag, false);
            _logger.LogInformation("Successfully processed document {DocumentId} | CorrelationId: {CorrelationId}", 
                anonymizedEvent.DocumentId, correlationId);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing message | CorrelationId: {CorrelationId}", correlationId);
            
            // Nack with requeue for transient errors
            _channel?.BasicNack(eventArgs.DeliveryTag, false, true);
        }
    }

    private async Task ProcessDocumentAnonymizedEvent(DocumentAnonymizedEvent anonymizedEvent, string correlationId)
    {
        using var scope = _serviceProvider.CreateScope();
        var documentRepository = scope.ServiceProvider.GetRequiredService<IDocumentRepository>();

        try
        {
            // Get the document
            var document = await documentRepository.GetByIdAsync(anonymizedEvent.DocumentId.ToString());
            if (document == null)
            {
                _logger.LogWarning("Document {DocumentId} not found | CorrelationId: {CorrelationId}", 
                    anonymizedEvent.DocumentId, correlationId);
                return;
            }

            // Update document with anonymization results
            document.Status = ProcessingStatus.Anonymized;
            document.AnonymizedFilePath = anonymizedEvent.AnonymizedFilePath;
            
            // Convert SensitiveDataDetection to SensitiveData
            document.DetectedSensitiveData.Clear();
            foreach (var detection in anonymizedEvent.DetectedData)
            {
                document.DetectedSensitiveData.Add(new SensitiveData
                {
                    Type = detection.Type,
                    OriginalValue = detection.OriginalValue,
                    AnonymizedValue = $"[{detection.Type.ToString().ToUpper()}]", // Simple placeholder
                    Confidence = detection.Confidence,
                    Location = new DataLocation
                    {
                        StartIndex = detection.StartPosition,
                        EndIndex = detection.EndPosition
                    }
                });
            }

            await documentRepository.UpdateAsync(document);

            _logger.LogInformation("Updated document {DocumentId} status to Anonymized with {DetectedCount} sensitive data items | CorrelationId: {CorrelationId}",
                anonymizedEvent.DocumentId, anonymizedEvent.DetectedData.Count, correlationId);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to update document {DocumentId} | CorrelationId: {CorrelationId}", 
                anonymizedEvent.DocumentId, correlationId);
            throw; // Re-throw to trigger nack with requeue
        }
    }

    public override async Task StopAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("DocumentResultConsumer stopping...");
        
        try
        {
            _channel?.Close();
            _connection?.Close();
            await base.StopAsync(cancellationToken);
            _logger.LogInformation("DocumentResultConsumer stopped successfully");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error stopping DocumentResultConsumer");
        }
    }

    public new void Dispose()
    {
        try
        {
            _channel?.Dispose();
            _connection?.Dispose();
            base.Dispose();
            _logger.LogInformation("DocumentResultConsumer disposed");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error disposing DocumentResultConsumer");
        }
    }
}