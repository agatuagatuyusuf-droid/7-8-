using System;
using System.IO;
using Microsoft.Extensions.Configuration;

namespace AutoDoor.CoreService.Common;

public class AppSettings
{
    public LicenseSettings License { get; set; } = new();
    public IpcSettings Ipc { get; set; } = new();
    public LoggingSettings Logging { get; set; } = new();

    public static AppSettings Load()
    {
        var basePath = AppDomain.CurrentDomain.BaseDirectory;
        var config = new ConfigurationBuilder()
            .SetBasePath(basePath)
            .AddJsonFile("appsettings.json", optional: false, reloadOnChange: false)
            .Build();

        var settings = new AppSettings();
        config.Bind(settings);
        return settings;
    }
}

public class LicenseSettings
{
    public string ServerUrl { get; set; } = "https://YOUR-DOMAIN.com";
    public string ProductId { get; set; } = "autodoor_pro";
    public string PublicKey { get; set; } = "";
    public string CacheDir { get; set; } = "%APPDATA%/AutoDoorPro/license";
    public int OfflineHours { get; set; } = 72;
    public int AutoRefreshMinutes { get; set; } = 60;

    public string ResolvedCacheDir => CacheDir.Replace("%APPDATA%", Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData));
}

public class IpcSettings
{
    public string Host { get; set; } = "127.0.0.1";
    public int Port { get; set; } = 19527;
    public int MaxConcurrentRequests { get; set; } = 16;
}

public class LoggingSettings
{
    public string Level { get; set; } = "Information";
    public string Directory { get; set; } = "%APPDATA%/AutoDoorPro/logs";

    public string ResolvedDirectory => Directory.Replace("%APPDATA%", Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData));
}
