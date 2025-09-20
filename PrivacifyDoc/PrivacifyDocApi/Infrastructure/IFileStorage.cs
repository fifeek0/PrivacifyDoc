using System.IO;
using System.Threading;
using System.Threading.Tasks;

namespace PrivacifyDoc.Api.Infrastructure
{
    public interface IFileStorage
    {
        Task<string> SaveFileAsync(Stream fileStream, string fileName, CancellationToken cancellationToken = default);
    }
}
