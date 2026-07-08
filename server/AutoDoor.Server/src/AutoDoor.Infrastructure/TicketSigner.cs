using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace AutoDoor.Server.Infrastructure;

public class TicketSigner
{
    private readonly RSA _rsa;

    public TicketSigner()
    {
        _rsa = RSA.Create(2048);
        LoadOrGenerateKey();
    }

    private void LoadOrGenerateKey()
    {
        // DEV ONLY: generated key is for local development only.
        var envKey = Environment.GetEnvironmentVariable("TICKET_PRIVATE_KEY");
        if (!string.IsNullOrEmpty(envKey))
        {
            try { _rsa.ImportFromPem(envKey); return; }
            catch { }
        }

        var envPath = Environment.GetEnvironmentVariable("TICKET_KEY_PATH");
        if (!string.IsNullOrEmpty(envPath) && System.IO.File.Exists(envPath))
        {
            try { _rsa.ImportFromPem(System.IO.File.ReadAllText(envPath)); return; }
            catch { }
        }

        var defaultDir = System.IO.Path.Combine(AppContext.BaseDirectory, "keys");
        var defaultPath = System.IO.Path.Combine(defaultDir, "private_key.pem");
        if (System.IO.File.Exists(defaultPath))
        {
            try { _rsa.ImportFromPem(System.IO.File.ReadAllText(defaultPath)); return; }
            catch { }
        }

        System.IO.Directory.CreateDirectory(defaultDir);
        var privPem = _rsa.ExportRSAPrivateKeyPem();
        System.IO.File.WriteAllText(defaultPath, privPem);
        var pubPath = System.IO.Path.Combine(defaultDir, "public_key.pem");
        if (!System.IO.File.Exists(pubPath))
        {
            var pubPem = _rsa.ExportSubjectPublicKeyInfoPem();
            System.IO.File.WriteAllText(pubPath, pubPem);
        }
    }

    public string Sign(JsonElement ticketElement)
    {
        var canonicalJson = BuildCanonicalJson(ticketElement);
        var data = Encoding.UTF8.GetBytes(canonicalJson);
        var signature = _rsa.SignData(data, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        return Convert.ToBase64String(signature);
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

    public string GetPrivateKeyPem()
    {
        return _rsa.ExportRSAPrivateKeyPem();
    }
}
