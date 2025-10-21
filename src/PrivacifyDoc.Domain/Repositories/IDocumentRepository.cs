using PrivacifyDoc.Domain.Entities;

namespace PrivacifyDoc.Domain.Repositories;

public interface IDocumentRepository
{
    Task<Document?> GetByIdAsync(string id, CancellationToken cancellationToken = default);
    Task<string> CreateAsync(Document document, CancellationToken cancellationToken = default);
    Task UpdateAsync(Document document, CancellationToken cancellationToken = default);
}