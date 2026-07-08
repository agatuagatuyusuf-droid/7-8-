using System;
using System.Security.Cryptography;
using System.Text;
using Microsoft.Win32;

namespace AutoDoor.CoreService.License;

public class MachineCodeProvider
{
    public string Generate()
    {
        var components = new StringBuilder();

        try
        {
            using var key = Registry.LocalMachine.OpenSubKey(
                @"SOFTWARE\Microsoft\Cryptography");
            if (key?.GetValue("MachineGuid") is string guid)
                components.Append(guid);
        }
        catch { }

        try
        {
            using var key = Registry.LocalMachine.OpenSubKey(
                @"HARDWARE\DESCRIPTION\System\CentralProcessor\0");
            if (key?.GetValue("ProcessorNameString") is string cpu)
                components.Append(cpu);
        }
        catch { }

        try
        {
            var drive = Environment.GetFolderPath(Environment.SpecialFolder.System)
                .Substring(0, 2);
            using var key = Registry.LocalMachine.OpenSubKey(
                @"HARDWARE\DEVICEMAP\Scsi\Scsi Port 0\Scsi Bus 0\Target Id 0\Logical Unit Id 0");
            if (key?.GetValue("SerialNumber") is string serial)
                components.Append(serial);
        }
        catch { }

        try
        {
            components.Append(Environment.UserName);
            components.Append(Environment.MachineName);
        }
        catch { }

        var input = components.ToString();
        if (string.IsNullOrEmpty(input))
            input = Guid.NewGuid().ToString();

        var hash = SHA256.HashData(Encoding.UTF8.GetBytes(input));
        return Convert.ToHexString(hash).ToLowerInvariant();
    }
}
