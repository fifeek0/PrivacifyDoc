using System;
using System.Threading;
using System.Threading.Tasks;
using MongoDB.Driver;
using PrivacifyDoc.Api.CQRS.Commands;
using PrivacifyDoc.Api.Infrastructure;
using PrivacifyDoc.Domain.Models;

namespace PrivacifyDoc.Api.CQRS.Handlers
{
    public record DocumentUploadedEvent(string DocumentId, string FilePath);

    public class AnonymizeDocumentCommandHandler : ICommandHandler<AnonymizeDocumentCommand>
    {
        private readonly IMongoCollection<Document> _documentsCollection;
        private readonly IFileStorage _fileStorage;
        private readonly IMessagePublisher _messagePublisher;

        public AnonymizeDocumentCommandHandler(IMongoDatabase database, IFileStorage fileStorage, IMessagePublisher messagePublisher)
        {
            _documentsCollection = database.GetCollection<Document>("Documents");
            _fileStorage = fileStorage;
            _messagePublisher = messagePublisher;
        }

        public async Task HandleAsync(AnonymizeDocumentCommand command, CancellationToken cancellationToken)
        {
            var originalFilePath = await _fileStorage.SaveFileAsync(command.DocumentStream, command.OriginalFileName, cancellationToken);

            var document = new Document
            {
                OriginalFileName = command.OriginalFileName,
                ContentType = command.ContentType,
                UploadDate = DateTime.UtcNow,
                Status = ProcessingStatus.Uploaded,
                OriginalFilePath = originalFilePath,
                Settings = command.Settings
            };

            await _documentsCollection.InsertOneAsync(document, cancellationToken: cancellationToken);

            await _messagePublisher.PublishAsync(new DocumentUploadedEvent(document.Id, document.OriginalFilePath), "document_upload_completed");
        }
    }
}
