using System;
using System.Collections.Generic;

namespace AutoDoor.Server.Api.Dtos.Admin;

public class LoginRequest
{
    public string Username { get; set; } = "";
    public string Password { get; set; } = "";
}

public class LoginResponse
{
    public bool Success { get; set; }
    public string Token { get; set; } = "";
    public string ExpiresAt { get; set; } = "";
}

public class UserDto
{
    public Guid Id { get; set; }
    public string UserCode { get; set; } = "";
    public string Name { get; set; } = "";
    public string Email { get; set; } = "";
}

public class CreateUserRequest
{
    public string Name { get; set; } = "";
    public string Email { get; set; } = "";
}

public class UpdateUserRequest
{
    public string Name { get; set; } = "";
    public string Email { get; set; } = "";
}

public class ProductDto
{
    public Guid Id { get; set; }
    public string ProductId { get; set; } = "";
    public string Name { get; set; } = "";
    public string Description { get; set; } = "";
}

public class CreateProductRequest
{
    public string ProductId { get; set; } = "";
    public string Name { get; set; } = "";
    public string Description { get; set; } = "";
}

public class UpdateProductRequest
{
    public string Name { get; set; } = "";
    public string Description { get; set; } = "";
}

public class GenerateActivationCodesRequest
{
    public int Count { get; set; } = 1;
    public string ProductId { get; set; } = "autodoor_pro";
    public string Edition { get; set; } = "pro";
    public int DurationDays { get; set; } = 365;
    public int MachineLimit { get; set; } = 1;
    public List<string> Features { get; set; } = new();
    public DateTime? ExpireAt { get; set; }
}

public class ActivationCodeDto
{
    public Guid Id { get; set; }
    public string Code { get; set; } = "";
    public string Edition { get; set; } = "";
    public int DurationDays { get; set; }
    public int MachineLimit { get; set; }
    public bool Used { get; set; }
    public bool Disabled { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? UsedAt { get; set; }
}

public class LicenseDto
{
    public Guid Id { get; set; }
    public string LicenseId { get; set; } = "";
    public string LicenseType { get; set; } = "";
    public string Edition { get; set; } = "";
    public DateTime ExpireAt { get; set; }
    public bool Active { get; set; }
    public bool Banned { get; set; }
    public string BanReason { get; set; } = "";
    public int MachineLimit { get; set; }
    public int OfflineDays { get; set; }
}

public class ExtendLicenseRequest
{
    public int Days { get; set; }
}

public class BanMachineRequest
{
    public string Reason { get; set; } = "";
}

public class CreateOrderRequest
{
    public string OrderNo { get; set; } = "";
    public string UserCode { get; set; } = "";
    public string ProductId { get; set; } = "autodoor_pro";
    public string Edition { get; set; } = "pro";
    public decimal Amount { get; set; }
    public string PayMethod { get; set; } = "manual";
    public string Remark { get; set; } = "";
}

public class OrderDto
{
    public Guid Id { get; set; }
    public string OrderNo { get; set; } = "";
    public string Status { get; set; } = "";
    public decimal Amount { get; set; }
    public string PayMethod { get; set; } = "";
    public DateTime CreatedAt { get; set; }
}

public class VersionReleaseDto
{
    public Guid Id { get; set; }
    public string Version { get; set; } = "";
    public string Changelog { get; set; } = "";
    public string DownloadUrl { get; set; } = "";
    public bool ForceUpdate { get; set; }
    public string MinSupportedVersion { get; set; } = "";
}

public class MachineDto
{
    public Guid Id { get; set; }
    public string MachineCode { get; set; } = "";
    public string MachineName { get; set; } = "";
    public bool Banned { get; set; }
    public string BanReason { get; set; } = "";
    public DateTime RegisteredAt { get; set; }
    public DateTime LastHeartbeat { get; set; }
}

public class AuditLogDto
{
    public Guid Id { get; set; }
    public string AdminId { get; set; } = "";
    public string Action { get; set; } = "";
    public string TargetType { get; set; } = "";
    public string TargetId { get; set; } = "";
    public string Ip { get; set; } = "";
    public string UserAgent { get; set; } = "";
    public string DetailsJson { get; set; } = "";
    public DateTime CreatedAt { get; set; }
}
