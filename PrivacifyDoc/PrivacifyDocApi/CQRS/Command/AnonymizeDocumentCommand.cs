using System.IO;
using PrivacifyDoc.Api.CQRS;
using PrivacifyDoc.Domain.Models;

namespace PrivacifyDoc.Api.CQRS.Commands
{
    public class AnonymizeDocumentCommand : ICommand
    {
        public Stream DocumentStream { get; set; } = null!;
        public string OriginalFileName { get; set; } = null!;
        public string ContentType { get; set; } = null!;
        public AnonymizationSettings Settings { get; set; } = null!;
    }
}
