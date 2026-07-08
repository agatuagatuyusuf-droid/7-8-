using System;
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

    public string GetPublicKeyPem()
    {
        return _rsa.ExportSubjectPublicKeyInfoPem();
    }

    public string GetPrivateKeyPem()
    {
        return _rsa.ExportRSAPrivateKeyPem();
    }
}
