using Microsoft.Extensions.Logging;
using PrivacifyDoc.Application.Commands;
using PrivacifyDoc.Application.Interfaces;
using PrivacifyDoc.Domain.Entities;
using PrivacifyDoc.Domain.Enums;
using PrivacifyDoc.Domain.Events;
using PrivacifyDoc.Domain.Repositories;
using PrivacifyDoc.Domain.Services;

namespace PrivacifyDoc.Application.Handlers;

public class UploadDocumentCommandHandler : ICommandHandler<UploadDocumentCommand>
{
    private readonly IDocumentRepository _documentRepository;
    private readonly IFileStorage _fileStorage;
    private readonly IMessagePublisher _messagePublisher;
    private readonly ILogger<UploadDocumentCommandHandler> _logger;

    public UploadDocumentCommandHandler(
        IDocumentRepository documentRepository,
        IFileStorage fileStorage,
        IMessagePublisher messagePublisher,
        ILogger<UploadDocumentCommandHandler> logger)
    {
        _documentRepository = documentRepository;
        _fileStorage = fileStorage;
        _messagePublisher = messagePublisher;
        _logger = logger;
    }

    public async Task HandleAsync(UploadDocumentCommand command, CancellationToken cancellationToken = default)
    {
        var correlationId = Guid.NewGuid().ToString();
        _logger.LogInformation("Processing document upload: {FileName} | CorrelationId: {CorrelationId}", 
            command.OriginalFileName, correlationId);

        try
        {
            // Save file to storage
            var filePath = await _fileStorage.SaveFileAsync(
                command.DocumentStream, 
                command.OriginalFileName, 
                cancellationToken);

            _logger.LogInformation("File saved to: {FilePath} | CorrelationId: {CorrelationId}", 
                filePath, correlationId);

            // Create document entity
            var document = new Document
            {
                Id = Guid.NewGuid().ToString(),
                OriginalFileName = command.OriginalFileName,
                ContentType = command.ContentType,
                UploadDate = DateTime.UtcNow,
                Status = ProcessingStatus.Uploaded,
                OriginalFilePath = filePath,
                Settings = command.Settings
            };

            // Save to database
            var documentId = await _documentRepository.CreateAsync(document, cancellationToken);
            document.Id = documentId;

            _logger.LogInformation("Document created in database with ID: {DocumentId} | CorrelationId: {CorrelationId}", 
                documentId, correlationId);

            // Get file size for event
            command.DocumentStream.Position = 0;
            var fileSize = command.DocumentStream.Length;

            // Publish event to start OCR processing
            var uploadedEvent = new DocumentUploadedEvent(
                DocumentId: Guid.Parse(documentId),
                OriginalFileName: command.OriginalFileName,
                FilePath: filePath,
                FileSize: fileSize,
                ContentType: command.ContentType,
                UploadedAt: DateTime.UtcNow
            );

            await _messagePublisher.PublishAsync(uploadedEvent, "document.uploaded");

            _logger.LogInformation("Published DocumentUploadedEvent for document {DocumentId} | CorrelationId: {CorrelationId}", 
                documentId, correlationId);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to process document upload: {FileName} | CorrelationId: {CorrelationId}", 
                command.OriginalFileName, correlationId);
            throw;
        }
    }
}