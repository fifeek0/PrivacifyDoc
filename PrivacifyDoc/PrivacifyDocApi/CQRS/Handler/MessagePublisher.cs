using System.Threading.Tasks;

namespace PrivacifyDoc.Api.CQRS.Handlers
{
    public interface IMessagePublisher
    {
        Task PublishAsync<T>(T message, string queueName);
    }

    public class RabbitMqPublisher : IMessagePublisher
    {
        public Task PublishAsync<T>(T message, string queueName)
        {
            // Logika RabbitMQ
            return Task.CompletedTask;
        }
    }
}
