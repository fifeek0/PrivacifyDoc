namespace PrivacifyDoc.Domain.Events;

public record TextExtractedEvent(
    Guid DocumentId,
    string ExtractedText,
    int PageCount,
    DateTime ExtractedAt
);