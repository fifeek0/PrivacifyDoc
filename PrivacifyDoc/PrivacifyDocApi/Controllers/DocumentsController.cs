using System.IO;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using PrivacifyDoc.Api.CQRS.Commands;
using PrivacifyDoc.Api.CQRS.Dispatcher;
using PrivacifyDoc.Domain.Models;

namespace PrivacifyDoc.Api.Controllers
{
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
        public async Task<IActionResult> UploadDocument(IFormFile file, [FromForm] AnonymizationSettings settings)
        {
            if (file == null || file.Length == 0) return BadRequest("File not provided.");

            await using var stream = new MemoryStream();
            await file.CopyToAsync(stream);
            stream.Position = 0;

            var command = new AnonymizeDocumentCommand
            {
                DocumentStream = stream,
                OriginalFileName = file.FileName,
                ContentType = file.ContentType,
                Settings = settings
            };

            await _dispatcher.SendAsync(command);
            
            return Accepted("Document processing started.");
        }
    }
}