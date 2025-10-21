using Microsoft.Extensions.Logging;
using PrivacifyDoc.Application.Interfaces;
using PrivacifyDoc.Application.Queries;
using PrivacifyDoc.Domain.Enums;
using PrivacifyDoc.Domain.Repositories;

namespace PrivacifyDoc.Application.Handlers;

public class GetDocumentStatusQueryHandler : IQueryHandler<GetDocumentStatusQuery, DocumentStatusResponse?>
{
    private readonly IDocumentRepository _documentRepository;
    private readonly ILogger<GetDocumentStatusQueryHandler> _logger;

    public GetDocumentStatusQueryHandler(
        IDocumentRepository documentRepository,
        ILogger<GetDocumentStatusQueryHandler> logger)
    {
        _documentRepository = documentRepository;
        _logger = logger;
    }

    public async Task<DocumentStatusResponse?> HandleAsync(GetDocumentStatusQuery query, CancellationToken cancellationToken = default)
    {
        try
        {
            var document = await _documentRepository.GetByIdAsync(query.DocumentId.ToString(), cancellationToken);
            
            if (document == null)
            {
                _logger.LogWarning("Document {DocumentId} not found", query.DocumentId);
                return null;
            }

            var progress = CalculateProgress(document.Status);

            return new DocumentStatusResponse
            {
                DocumentId = query.DocumentId,
                Status = document.Status,
                Progress = progress,
                DetectedDataCount = document.DetectedSensitiveData.Count,
                ErrorMessage = document.ErrorMessage
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get status for document {DocumentId}", query.DocumentId);
            throw;
        }
    }

    private static int CalculateProgress(ProcessingStatus status)
    {
        return status switch
        {
            ProcessingStatus.Uploaded => 25,
            ProcessingStatus.Processing => 50,
            ProcessingStatus.OCRCompleted => 75,
            ProcessingStatus.DataDetected => 85,
            ProcessingStatus.Anonymized => 100,
            ProcessingStatus.Error => 0,
            _ => 0
        };
    }
}