namespace PrivacifyDocCore.Domain
{
    public class File
    {
        public string GenerateTempFile()
        {
            string tempFilePath = System.IO.Path.GetTempFileName();
            return tempFilePath;
        }
    }
}