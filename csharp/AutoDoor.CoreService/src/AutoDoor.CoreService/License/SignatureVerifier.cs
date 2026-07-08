using System;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace AutoDoor.CoreService.License;

public class SignatureVerifier
{
    // Placeholder public key - replace with actual Ed25519/RSA public key
    private readonly byte[] _publicKey;

    public SignatureVerifier()
    {
        // TODO: Load actual public key from secure storage
        _publicKey = Array.Empty<byte>();
    }

    public bool Verify(JsonElement ticketElement)
    {
        try
        {
            if (!ticketElement.TryGetProperty("signature", out var sigProp))
                return false;

            var signature = Convert.FromBase64String(sigProp.GetString() ?? "");

            // Create a copy without signature for verification
            using var doc = JsonDocument.Parse(ticketElement.GetRawText());
            var clone = doc.RootElement.Clone();

            // TODO: Implement actual signature verification
            // For now, return true if signature exists and is non-empty
            return signature.Length > 0;
        }
        catch
        {
            return false;
        }
    }
}
