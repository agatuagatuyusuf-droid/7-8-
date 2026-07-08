using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace AutoDoor.CoreService.License;

public class SignatureVerifier
{
    private readonly RSA _rsa;

    public SignatureVerifier()
    {
        _rsa = RSA.Create(2048);
        var pem = LoadPublicKeyPem();
        if (!string.IsNullOrEmpty(pem))
        {
            try { _rsa.ImportFromPem(pem); }
            catch { }
        }
    }

    private static string LoadPublicKeyPem()
    {
        var envKey = Environment.GetEnvironmentVariable("TICKET_PUBLIC_KEY");
        if (!string.IsNullOrEmpty(envKey))
            return envKey;

        var envPath = Environment.GetEnvironmentVariable("TICKET_KEY_PATH");
        if (!string.IsNullOrEmpty(envPath) && System.IO.File.Exists(envPath))
            return System.IO.File.ReadAllText(envPath);

        var defaultPath = System.IO.Path.Combine(
            AppContext.BaseDirectory, "keys", "public_key.pem");
        if (System.IO.File.Exists(defaultPath))
            return System.IO.File.ReadAllText(defaultPath);

        return "";
    }

    public bool Verify(JsonElement ticketElement)
    {
        try
        {
            if (!ticketElement.TryGetProperty("signature", out var sigProp))
                return false;

            var signature = Convert.FromBase64String(sigProp.GetString() ?? "");
            if (signature.Length == 0)
                return false;

            var canonicalJson = BuildCanonicalJson(ticketElement);
            var data = Encoding.UTF8.GetBytes(canonicalJson);

            return _rsa.VerifyData(data, signature, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        }
        catch
        {
            return false;
        }
    }

    private static string BuildCanonicalJson(JsonElement ticketElement)
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
}
