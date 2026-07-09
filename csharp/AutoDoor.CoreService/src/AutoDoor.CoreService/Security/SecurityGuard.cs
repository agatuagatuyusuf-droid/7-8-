using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Security.Cryptography;

namespace AutoDoor.CoreService.Security;

public static class SecurityGuard
{
    public static bool IsDebuggingDetected()
    {
        if (Debugger.IsAttached)
        {
            return true;
        }

        try
        {
            if (IsDebuggerPresent())
            {
                return true;
            }
        }
        catch
        {
        }

        return false;
    }

    public static void ExitIfDebugging(LoginSessionService? sessions = null)
    {
        if (!IsDebuggingDetected())
        {
            return;
        }

        try
        {
            sessions?.ClearAll();
            WriteSecurityLog("DEBUGGER_DETECTED", "Debugger detected. CoreService exits itself.");
        }
        catch
        {
        }

        Environment.Exit(173);
    }

    public static bool VerifySelfHash(string expectedSha256)
    {
        if (string.IsNullOrWhiteSpace(expectedSha256))
        {
            return true;
        }

        try
        {
            var path = Assembly.GetExecutingAssembly().Location;
            if (string.IsNullOrWhiteSpace(path) || !File.Exists(path))
            {
                return false;
            }

            using var stream = File.OpenRead(path);
            var hash = SHA256.HashData(stream);
            var actual = Convert.ToHexString(hash).ToLowerInvariant();

            return string.Equals(
                actual,
                expectedSha256.ToLowerInvariant(),
                StringComparison.OrdinalIgnoreCase
            );
        }
        catch
        {
            return false;
        }
    }

    public static void WriteSecurityLog(string eventType, string message)
    {
        try
        {
            var dir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                "AutoDoorPro",
                "logs"
            );

            Directory.CreateDirectory(dir);

            var path = Path.Combine(dir, "security.log");
            var line = $"{DateTime.UtcNow:O} [{eventType}] {message}{Environment.NewLine}";
            File.AppendAllText(path, line);
        }
        catch
        {
        }
    }

    [DllImport("kernel32.dll")]
    private static extern bool IsDebuggerPresent();
}
