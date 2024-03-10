using Microsoft.AspNetCore.Mvc;

namespace PrivacifyDoc.Controllers;

public class FileController:Controller
{
    /// This is a constructor for the FileController class.
    /// It creates an instance of the FileController class.
    /// /
    public FileController()
    {

    }
    [HttpPost]
    public async Task<IActionResult> UploadFile(IFormFile? file)
    {
        if (file == null || file.Length == 0) {
            return Content("file not selected");
        }

        var path = Path.Combine(
            Directory.GetCurrentDirectory(),
            "wwwroot",
            file.FileName);
        await using (var stream = new FileStream(path, FileMode.Create)) {
            await file.CopyToAsync(stream);
        }

        return RedirectToAction("Index");
    }
}
