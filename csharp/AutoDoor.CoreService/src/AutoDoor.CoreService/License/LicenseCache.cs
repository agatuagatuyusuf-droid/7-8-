using System;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace AutoDoor.CoreService.License;

public class LicenseCache
{
    private readonly string _cacheDir;
    private readonly string _cacheFile;

    public LicenseCache()
    {
        var appData = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
        _cacheDir = Path.Combine(appData, "AutoDoorPro", "license");
        _cacheFile = Path.Combine(_cacheDir, "cache.dat");
    }

    public void Save(string ticketJson)
    {
        try
        {
            Directory.CreateDirectory(_cacheDir);
            var encrypted = ProtectedData.Protect(
                Encoding.UTF8.GetBytes(ticketJson),
                null,
                DataProtectionScope.CurrentUser);
            File.WriteAllBytes(_cacheFile, encrypted);
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"License cache save failed: {ex.Message}");
        }
    }

    public string? Load()
    {
        try
        {
            if (!File.Exists(_cacheFile)) return null;

            var encrypted = File.ReadAllBytes(_cacheFile);
            var decrypted = ProtectedData.Unprotect(
                encrypted,
                null,
                DataProtectionScope.CurrentUser);
            return Encoding.UTF8.GetString(decrypted);
        }
        catch
        {
            return null;
        }
    }

    public void Clear()
    {
        try
        {
            if (File.Exists(_cacheFile))
                File.Delete(_cacheFile);
        }
        catch { }
    }

    public bool IsWithinOfflinePeriod(string ticketJson)
    {
        try
        {
            using var doc = JsonDocument.Parse(ticketJson);
            var root = doc.RootElement;

            if (!root.TryGetProperty("offline_until", out var offlineProp))
                return false;

            var offlineUntil = DateTime.Parse(offlineProp.GetString() ?? "");
            return DateTime.UtcNow <= offlineUntil;
        }
        catch
        {
            return false;
        }
    }
}
