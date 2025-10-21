using System.Threading;
using System.Threading.Tasks;
using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;
using MongoDB.Driver;
using PrivacifyDoc.Domain.Repositories;
using PrivacifyDoc.Domain.Entities;

namespace PrivacifyDoc.Infrastructure.Persistence;

// MongoDB-specific Document model with attributes
public class MongoDocument : Document
{
    [BsonId]
    [BsonRepresentation(BsonType.ObjectId)]
    public new string Id { get; set; } = null!;
}

public class DocumentRepository : IDocumentRepository
{
    private readonly IMongoCollection<MongoDocument> _collection;

    public DocumentRepository(IMongoDatabase database)
    {
        _collection = database.GetCollection<MongoDocument>("Documents");
    }

    public async Task<Document?> GetByIdAsync(string id, CancellationToken cancellationToken = default)
    {
        var mongoDoc = await _collection.Find(d => d.Id == id).FirstOrDefaultAsync(cancellationToken);
        return mongoDoc; // Implicit conversion
    }

    public async Task<string> CreateAsync(Document document, CancellationToken cancellationToken = default)
    {
        var mongoDoc = new MongoDocument
        {
            OriginalFileName = document.OriginalFileName,
            ContentType = document.ContentType,
            UploadDate = document.UploadDate,
            Status = document.Status,
            ErrorMessage = document.ErrorMessage,
            OriginalFilePath = document.OriginalFilePath,
            AnonymizedFilePath = document.AnonymizedFilePath,
            Settings = document.Settings,
            DetectedSensitiveData = document.DetectedSensitiveData
        };

        await _collection.InsertOneAsync(mongoDoc, cancellationToken: cancellationToken);
        return mongoDoc.Id;
    }

    public async Task UpdateAsync(Document document, CancellationToken cancellationToken = default)
    {
        var filter = Builders<MongoDocument>.Filter.Eq(d => d.Id, document.Id);
        var update = Builders<MongoDocument>.Update
            .Set(d => d.Status, document.Status)
            .Set(d => d.ErrorMessage, document.ErrorMessage)
            .Set(d => d.AnonymizedFilePath, document.AnonymizedFilePath)
            .Set(d => d.DetectedSensitiveData, document.DetectedSensitiveData);

        await _collection.UpdateOneAsync(filter, update, cancellationToken: cancellationToken);
    }
}