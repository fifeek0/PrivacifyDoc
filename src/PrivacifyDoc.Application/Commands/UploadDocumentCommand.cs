using PrivacifyDoc.Application.Interfaces;
using PrivacifyDoc.Domain.Entities;

namespace PrivacifyDoc.Application.Commands;

public class UploadDocumentCommand : ICommand
{
    public Stream DocumentStream { get; set; } = null!;
    public string OriginalFileName { get; set; } = null!;
    public string ContentType { get; set; } = null!;
    public AnonymizationSettings Settings { get; set; } = null!;
}