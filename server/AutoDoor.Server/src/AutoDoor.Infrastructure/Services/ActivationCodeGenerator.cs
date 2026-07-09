using System;
using System.Security.Cryptography;

namespace AutoDoor.Server.Infrastructure.Services;

public static class ActivationCodeGenerator
{
    private const string Alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";

    public static string Generate()
    {
        return $"ADP-{Part()}-{Part()}-{Part()}";
    }

    private static string Part()
    {
        Span<byte> bytes = stackalloc byte[4];
        RandomNumberGenerator.Fill(bytes);
        var chars = new char[4];
        for (int i = 0; i < 4; i++)
        {
            chars[i] = Alphabet[bytes[i] % Alphabet.Length];
        }
        return new string(chars);
    }
}
