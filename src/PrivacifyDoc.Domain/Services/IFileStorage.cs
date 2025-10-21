namespace PrivacifyDoc.Domain.Services;

public interface IFileStorage
{
    Task<string> SaveFileAsync(Stream fileStream, string fileName, CancellationToken cancellationToken = default);
}