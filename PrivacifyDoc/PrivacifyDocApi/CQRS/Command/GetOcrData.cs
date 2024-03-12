namespace PrivacifyDoc.CQRS.Command;

public class OcrDataRetriever
{
    private const string OcDataCollectionName = "OcrData";

    private readonly IMongoCollection<Option> _collection;

    // Constructor that initializes the MongoCollection required for operations
    public OcrDataRetriever(IMongoDatabase database)
    {
        _collection = database.GetCollection<Option>(OcDataCollectionName);
    }

    // Method to asynchronously retrieve a record with a specific 'id'
    public async Task<Option> GetAsync(string id)
    {
        return await _collection.Find(new BsonDocument("_id", new ObjectId(id))).FirstOrDefaultAsync();
    }
}