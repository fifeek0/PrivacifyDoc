using PrivacifyDoc.Application.Interfaces;
using PrivacifyDoc.Domain.Enums;

namespace PrivacifyDoc.Application.Commands;

public class UpdateDocumentStatusCommand : ICommand
{
    public Guid DocumentId { get; set; }
    public ProcessingStatus Status { get; set; }
    public string? ErrorMessage { get; set; }
    public string? AnonymizedFilePath { get; set; }
}