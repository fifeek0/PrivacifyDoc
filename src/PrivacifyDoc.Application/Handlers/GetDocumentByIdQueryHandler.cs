using Microsoft.Extensions.Logging;
using PrivacifyDoc.Application.Interfaces;
using PrivacifyDoc.Application.Queries;
using PrivacifyDoc.Domain.Entities;
using PrivacifyDoc.Domain.Repositories;

namespace PrivacifyDoc.Application.Handlers;

public class GetDocumentByIdQueryHandler : IQueryHandler<GetDocumentByIdQuery, Document?>
{
    private readonly IDocumentRepository _documentRepository;
    private readonly ILogger<GetDocumentByIdQueryHandler> _logger;

    public GetDocumentByIdQueryHandler(
        IDocumentRepository documentRepository,
        ILogger<GetDocumentByIdQueryHandler> logger)
    {
        _documentRepository = documentRepository;
        _logger = logger;
    }

    public async Task<Document?> HandleAsync(GetDocumentByIdQuery query, CancellationToken cancellationToken = default)
    {
        try
        {
            var document = await _documentRepository.GetByIdAsync(query.DocumentId.ToString(), cancellationToken);
            
            if (document == null)
            {
                _logger.LogWarning("Document {DocumentId} not found", query.DocumentId);
            }

            return document;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get document {DocumentId}", query.DocumentId);
            throw;
        }
    }
}