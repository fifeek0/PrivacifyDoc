using MongoDB.Bson;
using MongoDB.Driver;

namespace PrivacifyDocCore.Mongo;

/// <summary>
/// Class that provides services for MongoDB.
/// </summary>
public class MongoServices
{
    private IMongoCollection<BsonDocument> _collection; //Change BsonDocument to your data class

    public MongoServices()
    {
        MongoClient client = new("mongodb://localhost:27017"); //Replace with your Connection String
        var database = client.GetDatabase("YourDatabaseName");
        _collection = database.GetCollection<BsonDocument>("YourCollectionName");
    }

    public List<BsonDocument> GetAllDocuments() //Change BsonDocument to your data class
    {
        return _collection.Find(new BsonDocument()).ToList();
    }

    public BsonDocument GetDocument(string id) //Change BsonDocument to your data class
    {
        var filter = Builders<BsonDocument>.Filter.Eq("_id", id);
        return _collection.Find(filter).FirstOrDefault();
    }

    public void InsertDocument(BsonDocument document) //Change BsonDocument to your data class
    {
        _collection.InsertOne(document);
    }

    public void UpdateDocument(string id, BsonDocument document) //Change BsonDocument to your data class
    {
        var filter = Builders<BsonDocument>.Filter.Eq("_id", id);
        _collection.ReplaceOne(filter, document);
    }

    public void DeleteDocument(string id)
    {
        var filter = Builders<BsonDocument>.Filter.Eq("_id", id);
        _collection.DeleteOne(filter);
    }
}