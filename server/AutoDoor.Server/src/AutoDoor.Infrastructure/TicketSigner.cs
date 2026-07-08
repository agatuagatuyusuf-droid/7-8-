using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace AutoDoor.Server.Infrastructure;

public class TicketSigner
{
    private readonly RSA _rsa;
    private readonly bool _isProduction;
    private readonly bool _hasPrivateKey;

    public bool HasPrivateKey => _hasPrivateKey;

    public TicketSigner()
    {
        _rsa = RSA.Create(2048);
        _isProduction = Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT") == "Production";
        _hasPrivateKey = LoadOrGenerateKey();
    }

    private bool LoadOrGenerateKey()
    {
        // Production: must read from env var or file
        var envKey = Environment.GetEnvironmentVariable("AUTODOOR_SERVER_PRIVATE_KEY_PEM");
        if (!string.IsNullOrEmpty(envKey))
        {
            try { _rsa.ImportFromPem(envKey); return true; }
            catch { }
        }

        var envPath = Environment.GetEnvironmentVariable("AUTODOOR_SERVER_PRIVATE_KEY_PATH");
        if (!string.IsNullOrEmpty(envPath) && File.Exists(envPath))
        {
            try { _rsa.ImportFromPem(File.ReadAllText(envPath)); return true; }
            catch { }
        }

        var settingsPath = Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT") == "Development"
            ? ""
            : "";
        
        // Check appsettings Signing:PrivateKeyPath (handled by configuration, not direct file)
        // For now, rely on env vars for production

        if (_isProduction)
        {
            Console.Error.WriteLine("FATAL: Production environment requires a private key via AUTODOOR_SERVER_PRIVATE_KEY_PEM or AUTODOOR_SERVER_PRIVATE_KEY_PATH");
            Environment.Exit(1);
            return false;
        }

        // Development: generate ephemeral key
        Console.WriteLine("DEV ONLY: ephemeral signing key generated. Not suitable for production.");
        var defaultDir = Path.Combine(AppContext.BaseDirectory, "keys");
        Directory.CreateDirectory(defaultDir);
        var privPem = _rsa.ExportRSAPrivateKeyPem();
        File.WriteAllText(Path.Combine(defaultDir, "private_key.pem"), privPem);
        var pubPem = _rsa.ExportSubjectPublicKeyInfoPem();
        File.WriteAllText(Path.Combine(defaultDir, "public_key.pem"), pubPem);
        return true;
    }

    public string Sign(string canonicalJson)
    {
        var data = Encoding.UTF8.GetBytes(canonicalJson);
        var signature = _rsa.SignData(data, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        return Convert.ToBase64String(signature);
    }

    public bool Verify(string canonicalJson, string signature)
    {
        try
        {
            var data = Encoding.UTF8.GetBytes(canonicalJson);
            var sig = Convert.FromBase64String(signature);
            return _rsa.VerifyData(data, sig, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        }
        catch
        {
            return false;
        }
    }

    public static string BuildCanonicalJson(JsonElement ticketElement)
    {
        var fields = new Dictionary<string, JsonElement?>();
        foreach (var prop in ticketElement.EnumerateObject())
        {
            if (prop.Name != "signature")
                fields[prop.Name] = prop.Value.Clone();
        }

        var orderedKeys = fields.Keys.OrderBy(k => k).ToList();
        var sb = new StringBuilder();
        sb.Append('{');
        for (int i = 0; i < orderedKeys.Count; i++)
        {
            if (i > 0) sb.Append(',');
            var key = orderedKeys[i];
            sb.Append('"');
            sb.Append(key);
            sb.Append('"');
            sb.Append(':');
            var val = fields[key];
            if (val == null)
                sb.Append("null");
            else
                sb.Append(val.Value.GetRawText());
        }
        sb.Append('}');
        return sb.ToString();
    }

    public string GetPublicKeyPem()
    {
        return _rsa.ExportSubjectPublicKeyInfoPem();
    }
}