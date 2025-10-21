using PrivacifyDoc.Domain.Enums;

namespace PrivacifyDoc.Domain.Entities;

public class Document
{
    public string Id { get; set; } = null!;
    
    public string OriginalFileName { get; set; } = null!;
    
    public string ContentType { get; set; } = null!;
    
    public DateTime UploadDate { get; set; }
    
    public ProcessingStatus Status { get; set; }
    
    public string? ErrorMessage { get; set; }

    public string OriginalFilePath { get; set; } = null!;
    
    public string? AnonymizedFilePath { get; set; }
    
    public AnonymizationSettings Settings { get; set; } = new();
    
    public List<SensitiveData> DetectedSensitiveData { get; set; } = new();
}

public class AnonymizationSettings
{
    public List<SensitiveDataType> DataTypesToAnonymize { get; set; } = new();
    
    public AnonymizationMethod Method { get; set; }
    
    public Dictionary<string, string> Options { get; set; } = new();
}

public class SensitiveData
{
    public SensitiveDataType Type { get; set; }
    
    public string OriginalValue { get; set; } = null!;
    
    public string AnonymizedValue { get; set; } = null!;
    
    public DataLocation Location { get; set; } = null!;
    
    public double Confidence { get; set; }
}

public class DataLocation
{
    public int? PageNumber { get; set; }
    
    public Rectangle? BoundingBox { get; set; }
    
    public int? StartIndex { get; set; }
    
    public int? EndIndex { get; set; }
}

public class Rectangle
{
    public int X { get; set; }
    public int Y { get; set; }
    public int Width { get; set; }
    public int Height { get; set; }
}

public class DocumentAnonymizationStats
{
    public string DocumentId { get; set; } = null!;
    public int DetectedDataCount { get; set; }
}