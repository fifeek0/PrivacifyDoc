using PrivacifyDoc.Application.Interfaces;
using PrivacifyDoc.Domain.Enums;

namespace PrivacifyDoc.Application.Queries;

public class GetDocumentStatusQuery : IQuery<DocumentStatusResponse?>
{
    public Guid DocumentId { get; set; }
}

public class DocumentStatusResponse
{
    public Guid DocumentId { get; set; }
    public ProcessingStatus Status { get; set; }
    public int Progress { get; set; }
    public int DetectedDataCount { get; set; }
    public string? ErrorMessage { get; set; }
}