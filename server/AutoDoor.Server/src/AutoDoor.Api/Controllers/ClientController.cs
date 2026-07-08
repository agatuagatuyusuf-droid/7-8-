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
            .FirstOrDefaultAsync(a => a.Code == request.ActivationCode && !a.Used);

        if (activationCode == null)
            return Ok(new { success = false, error_code = "INVALID_CODE", message = "Invalid or already used activation code" });

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

        await _db.SaveChangesAsync();

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
            ["offline_until"] = DateTime.UtcNow.AddHours(72).ToString("o"),
            ["force_update_min_version"] = "1.6.0"
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
            ["features"] = features,
            ["issued_at"] = license.IssuedAt.ToString("o"),
            ["expire_at"] = license.ExpireAt.ToString("o"),
            ["offline_until"] = DateTime.UtcNow.AddHours(72).ToString("o"),
            ["force_update_min_version"] = "1.6.0"
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
            .FirstOrDefaultAsync(m => m.MachineCode == request.MachineCode);

        if (machine != null)
        {
            machine.LastHeartbeat = DateTime.UtcNow;
            await _db.SaveChangesAsync();
        }

        return Ok(new { success = true });
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

    public bool IsValid() => !string.IsNullOrWhiteSpace(ActivationCode) && !string.IsNullOrWhiteSpace(MachineCode);
}
public class RefreshRequest
{
    private string _machineCode = "";

    [System.Text.Json.Serialization.JsonPropertyName("machine_code")]
    public string MachineCode { get => _machineCode; set => _machineCode = value ?? ""; }

    [System.Text.Json.Serialization.JsonPropertyName("product_id")]
    public string ProductId { get; set; } = "autodoor_pro";
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
}
