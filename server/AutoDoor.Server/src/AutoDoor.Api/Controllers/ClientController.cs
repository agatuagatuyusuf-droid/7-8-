using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using AutoDoor.Server.Domain;
using AutoDoor.Server.Infrastructure;

namespace AutoDoor.Server.Api.Controllers;

[ApiController]
[Route("api/client")]
public class ClientController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly TicketSigner _signer;
    private readonly IConfiguration _configuration;

    public ClientController(AppDbContext db, TicketSigner signer, IConfiguration configuration)
    {
        _db = db;
        _signer = signer;
        _configuration = configuration;
    }

    [HttpPost("activate")]
    public async Task<IActionResult> Activate([FromBody] ActivateRequest request)
    {
        if (!request.IsValid())
            return Ok(new { success = false, error_code = "INVALID_INPUT", message = "activation_code and machine_code must not be empty" });

        var activationCode = await _db.ActivationCodes
            .FirstOrDefaultAsync(a => a.Code == request.ActivationCode && !a.Used && !a.Disabled);

        if (activationCode == null)
            return Ok(new { success = false, error_code = "INVALID_CODE", message = "Invalid, disabled, or already used activation code" });

        var existingMachine = await _db.Machines.FirstOrDefaultAsync(m => m.MachineCode == request.MachineCode);
        if (existingMachine != null && existingMachine.Banned)
            return Ok(new { success = false, error_code = "MACHINE_BANNED", message = "This machine has been banned" });

        var product = await _db.Products.FindAsync(activationCode.ProductId);
        if (product == null)
            return Ok(new { success = false, error_code = "PRODUCT_NOT_FOUND", message = "Product not found" });

        var userCode = $"USER-{Guid.NewGuid().ToString("N")[..8].ToUpperInvariant()}";
        var user = new User { UserCode = userCode, Name = "User" };
        _db.Users.Add(user);
        await _db.SaveChangesAsync();

        var licenseId = $"LIC-{Guid.NewGuid().ToString("N")[..8].ToUpperInvariant()}";
        var license = new License
        {
            LicenseId = licenseId,
            UserId = user.Id,
            ProductId = product.Id,
            Edition = activationCode.Edition,
            IssuedAt = DateTime.UtcNow,
            ExpireAt = DateTime.UtcNow.AddDays(activationCode.DurationDays),
            MachineLimit = activationCode.MachineLimit
        };
        _db.Licenses.Add(license);

        var machine = new Machine
        {
            LicenseId = license.Id,
            MachineCode = request.MachineCode,
            MachineName = request.MachineCode[..Math.Min(20, request.MachineCode.Length)],
            RegisteredAt = DateTime.UtcNow,
            LastHeartbeat = DateTime.UtcNow
        };
        _db.Machines.Add(machine);

        activationCode.Used = true;
        activationCode.UsedByUserId = user.Id;
        activationCode.UsedAt = DateTime.UtcNow;

        var productFeatures = await _db.Features
            .OrderBy(f => f.FeatureCode)
            .ToListAsync();
        foreach (var f in productFeatures)
        {
            _db.LicenseFeatures.Add(new LicenseFeature { LicenseId = license.Id, FeatureId = f.Id });
        }

        var sessionId = $"SES-{Guid.NewGuid().ToString("N")[..12].ToUpperInvariant()}";
        var session = new LicenseSession
        {
            SessionId = sessionId,
            LicenseId = license.Id,
            MachineCode = request.MachineCode,
            Ip = HttpContext.Connection.RemoteIpAddress?.ToString() ?? "",
            AppVersion = request.AppVersion,
            CoreVersion = request.CoreVersion,
            StartedAt = DateTime.UtcNow,
            LastSeenAt = DateTime.UtcNow
        };
        _db.LicenseSessions.Add(session);

        await _db.SaveChangesAsync();

        var latestRelease = await _db.VersionReleases
            .OrderByDescending(v => v.ReleasedAt)
            .FirstOrDefaultAsync();

        var ticketFields = new Dictionary<string, object?>
        {
            ["ticket_version"] = 1,
            ["product_id"] = product.ProductId,
            ["license_id"] = license.LicenseId,
            ["user_id"] = userCode,
            ["machine_code"] = request.MachineCode,
            ["edition"] = license.Edition,
            ["features"] = productFeatures.Select(f => f.FeatureCode).ToList(),
            ["issued_at"] = license.IssuedAt.ToString("o"),
            ["expire_at"] = license.ExpireAt.ToString("o"),
            ["offline_until"] = DateTime.UtcNow.AddDays(license.OfflineDays).ToString("o"),
            ["force_update_min_version"] = latestRelease?.MinSupportedVersion ?? "1.6.0",
            ["license_type"] = license.LicenseType,
            ["major_version_limit"] = license.MajorVersionLimit,
            ["session_id"] = sessionId
        };

        var payloadJson = JsonSerializer.Serialize(ticketFields);
        using var ticketDoc = JsonDocument.Parse(payloadJson);
        var canonicalJson = TicketSigner.BuildCanonicalJson(ticketDoc.RootElement);
        var signature = _signer.Sign(canonicalJson);

        var responseTicket = new Dictionary<string, object?>(ticketFields)
        {
            ["signature"] = signature
        };

        return Ok(new
        {
            success = true,
            ticket = responseTicket
        });
    }

    [HttpPost("refresh")]
    public async Task<IActionResult> Refresh([FromBody] RefreshRequest request)
    {
        var machine = await _db.Machines
            .Include("License.Product")
            .FirstOrDefaultAsync(m => m.MachineCode == request.MachineCode);

        if (machine == null || machine.License == null)
            return Ok(new { success = false, error_code = "MACHINE_NOT_FOUND", message = "Machine not registered" });

        var license = machine.License;
        if (license == null || !license.Active)
            return Ok(new { success = false, error_code = "LICENSE_INACTIVE", message = "License is not active" });

        if (license.ExpireAt < DateTime.UtcNow)
            return Ok(new { success = false, error_code = "LICENSE_EXPIRED", message = "License has expired" });

        machine.LastHeartbeat = DateTime.UtcNow;

        var latestRelease = await _db.VersionReleases
            .OrderByDescending(v => v.ReleasedAt)
            .FirstOrDefaultAsync();

        var session = await _db.LicenseSessions
            .Where(s => s.MachineCode == request.MachineCode && s.LicenseId == license.Id && s.Active)
            .OrderByDescending(s => s.LastSeenAt)
            .FirstOrDefaultAsync();

        var sessionId = session?.SessionId ?? $"SES-{Guid.NewGuid().ToString("N")[..12].ToUpperInvariant()}";

        if (session == null)
        {
            _db.LicenseSessions.Add(new LicenseSession
            {
                SessionId = sessionId,
                LicenseId = license.Id,
                MachineCode = request.MachineCode,
                Ip = HttpContext.Connection.RemoteIpAddress?.ToString() ?? "",
                AppVersion = request.AppVersion,
                CoreVersion = "",
                Active = true,
                StartedAt = DateTime.UtcNow,
                LastSeenAt = DateTime.UtcNow
            });
        }
        else
        {
            session.LastSeenAt = DateTime.UtcNow;
            session.AppVersion = request.AppVersion;
        }

        await _db.SaveChangesAsync();

        var features = await _db.LicenseFeatures
            .Where(lf => lf.LicenseId == license.Id)
            .Join(_db.Features, lf => lf.FeatureId, f => f.Id, (lf, f) => f.FeatureCode)
            .OrderBy(fc => fc)
            .ToListAsync();

        var ticketFields = new Dictionary<string, object?>
        {
            ["ticket_version"] = 1,
            ["product_id"] = license.Product.ProductId,
            ["license_id"] = license.LicenseId,
            ["user_id"] = (await _db.Users.FindAsync(license.UserId))?.UserCode ?? "",
            ["machine_code"] = request.MachineCode,
            ["edition"] = license.Edition,
            ["license_type"] = license.LicenseType,
            ["features"] = features,
            ["issued_at"] = license.IssuedAt.ToString("o"),
            ["expire_at"] = license.ExpireAt.ToString("o"),
            ["offline_until"] = DateTime.UtcNow.AddDays(license.OfflineDays).ToString("o"),
            ["force_update_min_version"] = latestRelease?.MinSupportedVersion ?? "",
            ["major_version_limit"] = license.MajorVersionLimit,
            ["session_id"] = sessionId
        };

        var payloadJson = JsonSerializer.Serialize(ticketFields);
        using var ticketDoc = JsonDocument.Parse(payloadJson);
        var canonicalJson = TicketSigner.BuildCanonicalJson(ticketDoc.RootElement);
        var signature = _signer.Sign(canonicalJson);

        var responseTicket = new Dictionary<string, object?>(ticketFields)
        {
            ["signature"] = signature
        };

        return Ok(new
        {
            success = true,
            ticket = responseTicket
        });
    }

    [HttpPost("status")]
    public async Task<IActionResult> Status([FromBody] StatusRequest request)
    {
        var machine = await _db.Machines
            .Include("License")
            .FirstOrDefaultAsync(m => m.MachineCode == request.MachineCode);

        if (machine?.License == null)
            return Ok(new { success = false, error_code = "NOT_ACTIVATED", message = "Not activated" });

        return Ok(new
        {
            success = true,
            activated = machine.License.Active,
            valid = machine.License.Active && machine.License.ExpireAt >= DateTime.UtcNow,
            expire_at = machine.License.ExpireAt.ToString("o"),
            edition = machine.License.Edition
        });
    }

    [HttpPost("deactivate")]
    public async Task<IActionResult> Deactivate([FromBody] DeactivateRequest request)
    {
        var machine = await _db.Machines
            .FirstOrDefaultAsync(m => m.MachineCode == request.MachineCode);

        if (machine != null)
        {
            _db.Machines.Remove(machine);
            await _db.SaveChangesAsync();
        }

        return Ok(new { success = true, message = "Deactivated" });
    }

    [HttpPost("heartbeat")]
    public async Task<IActionResult> Heartbeat([FromBody] HeartbeatRequest request)
    {
        var machine = await _db.Machines
            .Include("License")
            .FirstOrDefaultAsync(m => m.MachineCode == request.MachineCode);

        if (machine == null)
            return Ok(new
            {
                success = false,
                active = false,
                banned = false,
                force_update = false,
                error_code = "NOT_ACTIVATED",
                message = "Not activated"
            });

        var banned = machine.Banned || (machine.License?.Banned ?? false);
        var banReason = machine.Banned ? machine.BanReason : (machine.License?.BanReason ?? "");

        machine.LastHeartbeat = DateTime.UtcNow;

        if (!string.IsNullOrWhiteSpace(request.SessionId))
        {
            var session = await _db.LicenseSessions
                .FirstOrDefaultAsync(s => s.SessionId == request.SessionId && s.MachineCode == request.MachineCode);

            if (session != null)
            {
                session.LastSeenAt = DateTime.UtcNow;
                session.AppVersion = request.AppVersion;
                session.CoreVersion = request.CoreVersion;
                session.Ip = HttpContext.Connection.RemoteIpAddress?.ToString() ?? "";
            }
        }

        await _db.SaveChangesAsync();

        var latestRelease = await _db.VersionReleases
            .OrderByDescending(v => v.ReleasedAt)
            .FirstOrDefaultAsync();

        var forceUpdate = latestRelease?.ForceUpdate ?? false;

        return Ok(new
        {
            success = true,
            active = machine.License?.Active ?? false,
            banned,
            ban_reason = banReason,
            force_update = forceUpdate,
            latest_version = latestRelease?.Version ?? "",
            min_supported_version = latestRelease?.MinSupportedVersion ?? "",
            download_url = latestRelease?.DownloadUrl ?? "",
            message = banned ? banReason : ""
        });
    }

    [HttpGet("public-key")]
    public IActionResult PublicKey()
    {
        var env = Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT") ?? "Production";
        var exposeConfig = _configuration["License:ExposePublicKeyEndpoint"];
        var expose = exposeConfig?.Equals("true", StringComparison.OrdinalIgnoreCase) ?? false;
        
        if (env == "Development" || expose)
        {
            return Ok(new
            {
                success = true,
                public_key = _signer.GetPublicKeyPem()
            });
        }
        
        return NotFound(new { success = false, error_code = "NOT_FOUND", message = "Not available" });
    }

    [HttpGet("version/latest")]
    public async Task<IActionResult> LatestVersion()
    {
        var release = await _db.VersionReleases
            .OrderByDescending(v => v.ReleasedAt)
            .FirstOrDefaultAsync();

        if (release == null)
            return Ok(new { success = true, data = (object?)null });

        return Ok(new { success = true, data = new { release.Version, release.Changelog, release.DownloadUrl, release.ForceUpdate } });
    }
}

public class ActivateRequest
{
    private string _activationCode = "";
    private string _machineCode = "";

    [System.Text.Json.Serialization.JsonPropertyName("activation_code")]
    public string ActivationCode { get => _activationCode; set => _activationCode = value ?? ""; }

    [System.Text.Json.Serialization.JsonPropertyName("machine_code")]
    public string MachineCode { get => _machineCode; set => _machineCode = value ?? ""; }

    [System.Text.Json.Serialization.JsonPropertyName("product_id")]
    public string ProductId { get; set; } = "autodoor_pro";

    [System.Text.Json.Serialization.JsonPropertyName("app_version")]
    public string AppVersion { get; set; } = "";

    [System.Text.Json.Serialization.JsonPropertyName("core_version")]
    public string CoreVersion { get; set; } = "";

    public bool IsValid() => !string.IsNullOrWhiteSpace(ActivationCode) && !string.IsNullOrWhiteSpace(MachineCode);
}

public class RefreshRequest
{
    private string _machineCode = "";

    [System.Text.Json.Serialization.JsonPropertyName("machine_code")]
    public string MachineCode { get => _machineCode; set => _machineCode = value ?? ""; }

    [System.Text.Json.Serialization.JsonPropertyName("product_id")]
    public string ProductId { get; set; } = "autodoor_pro";

    [System.Text.Json.Serialization.JsonPropertyName("app_version")]
    public string AppVersion { get; set; } = "";
}
public class StatusRequest
{
    private string _machineCode = "";

    [System.Text.Json.Serialization.JsonPropertyName("machine_code")]
    public string MachineCode { get => _machineCode; set => _machineCode = value ?? ""; }
}
public class DeactivateRequest
{
    private string _machineCode = "";

    [System.Text.Json.Serialization.JsonPropertyName("machine_code")]
    public string MachineCode { get => _machineCode; set => _machineCode = value ?? ""; }
}
public class HeartbeatRequest
{
    private string _machineCode = "";

    [System.Text.Json.Serialization.JsonPropertyName("machine_code")]
    public string MachineCode { get => _machineCode; set => _machineCode = value ?? ""; }

    [System.Text.Json.Serialization.JsonPropertyName("session_id")]
    public string SessionId { get; set; } = "";

    [System.Text.Json.Serialization.JsonPropertyName("app_version")]
    public string AppVersion { get; set; } = "";

    [System.Text.Json.Serialization.JsonPropertyName("core_version")]
    public string CoreVersion { get; set; } = "";
}
