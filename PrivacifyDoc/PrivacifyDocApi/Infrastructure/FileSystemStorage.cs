using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;

namespace PrivacifyDoc.Api.Infrastructure
{
    public class FileSystemStorage : IFileStorage
    {
        private readonly string _storageBasePath;

        public FileSystemStorage(IConfiguration configuration)
        {
            _storageBasePath = configuration["Storage:BasePath"] ?? Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Storage");
            if (!Directory.Exists(_storageBasePath)) Directory.CreateDirectory(_storageBasePath);
        }

        public async Task<string> SaveFileAsync(Stream fileStream, string fileName, CancellationToken cancellationToken = default)
        {
            var uniqueFileName = $"{Guid.NewGuid()}_{fileName}";
            var filePath = Path.Combine(_storageBasePath, uniqueFileName);
            await using var fileStreamWriter = new FileStream(filePath, FileMode.Create);
            fileStream.Position = 0;
            await fileStream.CopyToAsync(fileStreamWriter, cancellationToken);
            return filePath; 
        }
    }
}
