namespace PrivacifyDoc.Domain.Events;

public record DocumentUploadedEvent(
    Guid DocumentId,
    string OriginalFileName,
    string FilePath,
    long FileSize,
    string ContentType,
    DateTime UploadedAt
);