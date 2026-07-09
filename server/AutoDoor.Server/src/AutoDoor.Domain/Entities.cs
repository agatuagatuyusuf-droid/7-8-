using System;
using System.Collections.Generic;

namespace AutoDoor.Server.Domain;

public class Admin
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Username { get; set; } = "";
    public string PasswordHash { get; set; } = "";
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}

public class User
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string UserCode { get; set; } = "";
    public string Email { get; set; } = "";
    public string Name { get; set; } = "";
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}

public class Product
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string ProductId { get; set; } = "";
    public string Name { get; set; } = "";
    public string Description { get; set; } = "";
}

public class Feature
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string FeatureCode { get; set; } = "";
    public string Name { get; set; } = "";
    public string Description { get; set; } = "";
}

public class License
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string LicenseId { get; set; } = "";
    public Guid UserId { get; set; }
    public Guid ProductId { get; set; }
    public Product? Product { get; set; }
    public string Edition { get; set; } = "pro";
    public DateTime IssuedAt { get; set; } = DateTime.UtcNow;
    public DateTime ExpireAt { get; set; }
    public int MachineLimit { get; set; } = 1;
    public bool Active { get; set; } = true;
    public string LicenseType { get; set; } = "yearly";
    public bool Banned { get; set; } = false;
    public string BanReason { get; set; } = "";
    public int OfflineDays { get; set; } = 3;
    public string MajorVersionLimit { get; set; } = "";
}

public class LicenseFeature
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid LicenseId { get; set; }
    public License? License { get; set; }
    public Guid FeatureId { get; set; }
    public Feature? Feature { get; set; }
}

public class Machine
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid LicenseId { get; set; }
    public License? License { get; set; }
    public string MachineCode { get; set; } = "";
    public string MachineName { get; set; } = "";
    public bool Banned { get; set; }
    public string BanReason { get; set; } = "";
    public DateTime RegisteredAt { get; set; } = DateTime.UtcNow;
    public DateTime LastHeartbeat { get; set; }
}

public class ActivationCode
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Code { get; set; } = "";
    public Guid? ProductId { get; set; }
    public Product? Product { get; set; }
    public string Edition { get; set; } = "pro";
    public int DurationDays { get; set; } = 365;
    public int MachineLimit { get; set; } = 1;
    public bool Used { get; set; }
    public Guid? UsedByUserId { get; set; }
    public DateTime? UsedAt { get; set; }
    public bool Disabled { get; set; } = false;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}

public class VersionRelease
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Version { get; set; } = "";
    public string ProductId { get; set; } = "autodoor_pro";
    public string Changelog { get; set; } = "";
    public string DownloadUrl { get; set; } = "";
    public bool ForceUpdate { get; set; }
    public string MinSupportedVersion { get; set; } = "";
    public DateTime ReleasedAt { get; set; } = DateTime.UtcNow;
}

public class AuditLog
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Action { get; set; } = "";
    public string AdminId { get; set; } = "";
    public string TargetType { get; set; } = "";
    public string TargetId { get; set; } = "";
    public string Ip { get; set; } = "";
    public string UserAgent { get; set; } = "";
    public string DetailsJson { get; set; } = "";
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
