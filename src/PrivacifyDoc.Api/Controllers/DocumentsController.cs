using System.IO;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using PrivacifyDoc.Application;
using PrivacifyDoc.Application.Commands;
using PrivacifyDoc.Application.Queries;
using PrivacifyDoc.Domain.Entities;

namespace PrivacifyDoc.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class DocumentsController : ControllerBase
{
    private readonly Dispatcher _dispatcher;

    public DocumentsController(Dispatcher dispatcher)
    {
        _dispatcher = dispatcher;
    }

    [HttpPost]
    public async Task<IActionResult> UploadDocument(IFormFile file, [FromForm] AnonymizationSettings? settings)
    {
        if (file == null || file.Length == 0) 
            return BadRequest("File not provided.");

        await using var stream = new MemoryStream();
        await file.CopyToAsync(stream);
        stream.Position = 0;

        var command = new UploadDocumentCommand
        {
            DocumentStream = stream,
            OriginalFileName = file.FileName,
            ContentType = file.ContentType,
            Settings = settings ?? new AnonymizationSettings()
        };

        await _dispatcher.SendAsync(command);
        
        return Accepted("Document processing started.");
    }

    [HttpGet("{id}/status")]
    public async Task<IActionResult> GetDocumentStatus(string id)
    {
        if (!System.Guid.TryParse(id, out var documentId))
            return BadRequest("Invalid document ID format.");

        var query = new GetDocumentStatusQuery { DocumentId = documentId };
        var result = await _dispatcher.QueryAsync(query);
        
        if (result == null)
            return NotFound();
            
        return Ok(result);
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetDocument(string id)
    {
        if (!System.Guid.TryParse(id, out var documentId))
            return BadRequest("Invalid document ID format.");

        var query = new GetDocumentByIdQuery { DocumentId = documentId };
        var document = await _dispatcher.QueryAsync(query);
        
        if (document == null)
            return NotFound();
            
        return Ok(document);
    }
}