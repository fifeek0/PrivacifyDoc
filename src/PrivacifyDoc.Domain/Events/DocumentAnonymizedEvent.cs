using PrivacifyDoc.Domain.Enums;

namespace PrivacifyDoc.Domain.Events;

public record DocumentAnonymizedEvent(
    Guid DocumentId,
    string AnonymizedFilePath,
    List<SensitiveDataDetection> DetectedData,
    DateTime AnonymizedAt
);

public record SensitiveDataDetection(
    SensitiveDataType Type,
    string OriginalValue,
    int StartPosition,
    int EndPosition,
    double Confidence
);