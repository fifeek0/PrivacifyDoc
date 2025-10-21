namespace PrivacifyDoc.Domain.Services;

public interface IMessagePublisher
{
    Task PublishAsync<T>(T message, string queueName);
}