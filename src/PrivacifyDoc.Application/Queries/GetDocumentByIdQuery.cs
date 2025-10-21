using PrivacifyDoc.Application.Interfaces;
using PrivacifyDoc.Domain.Entities;

namespace PrivacifyDoc.Application.Queries;

public class GetDocumentByIdQuery : IQuery<Document?>
{
    public Guid DocumentId { get; set; }
}