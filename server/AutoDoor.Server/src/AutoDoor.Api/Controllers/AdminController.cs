using System;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using AutoDoor.Server.Domain;
using AutoDoor.Server.Infrastructure;

namespace AutoDoor.Server.Api.Controllers;

[ApiController]
[Route("api/admin")]
public class AdminController : ControllerBase
{
    private readonly AppDbContext _db;

    public AdminController(AppDbContext db) => _db = db;

    [HttpPost("login")]
    public async Task<IActionResult> Login([FromBody] LoginRequest request)
    {
        var admin = await _db.Admins.FirstOrDefaultAsync(a => a.Username == request.Username);
        if (admin == null || !VerifyPassword(request.Password, admin.PasswordHash))
            return Unauthorized(new { success = false, message = "Invalid credentials" });

        return Ok(new { success = true, token = "dev-jwt-token" });
    }

    [HttpGet("dashboard")]
    public async Task<IActionResult> Dashboard()
    {
        return Ok(new
        {
            total_licenses = await _db.Licenses.CountAsync(),
            active_licenses = await _db.Licenses.CountAsync(l => l.Active),
            total_users = await _db.Users.CountAsync(),
            total_machines = await _db.Machines.CountAsync()
        });
    }

    // Users CRUD
    [HttpGet("users")] public async Task<IActionResult> GetUsers() => Ok(await _db.Users.ToListAsync());
    [HttpPost("users")] public async Task<IActionResult> CreateUser([FromBody] User user) { _db.Users.Add(user); await _db.SaveChangesAsync(); return Ok(user); }
    [HttpPut("users/{id}")] public async Task<IActionResult> UpdateUser(Guid id, [FromBody] User updated) { var user = await _db.Users.FindAsync(id); if (user == null) return NotFound(); user.Name = updated.Name; user.Email = updated.Email; await _db.SaveChangesAsync(); return Ok(user); }
    [HttpDelete("users/{id}")] public async Task<IActionResult> DeleteUser(Guid id) { var user = await _db.Users.FindAsync(id); if (user == null) return NotFound(); _db.Users.Remove(user); await _db.SaveChangesAsync(); return Ok(new { success = true }); }

    // Products CRUD
    [HttpGet("products")] public async Task<IActionResult> GetProducts() => Ok(await _db.Products.ToListAsync());
    [HttpPost("products")] public async Task<IActionResult> CreateProduct([FromBody] Product product) { _db.Products.Add(product); await _db.SaveChangesAsync(); return Ok(product); }
    [HttpPut("products/{id}")] public async Task<IActionResult> UpdateProduct(Guid id, [FromBody] Product updated) { var p = await _db.Products.FindAsync(id); if (p == null) return NotFound(); p.Name = updated.Name; p.Description = updated.Description; await _db.SaveChangesAsync(); return Ok(p); }
    [HttpDelete("products/{id}")] public async Task<IActionResult> DeleteProduct(Guid id) { var p = await _db.Products.FindAsync(id); if (p == null) return NotFound(); _db.Products.Remove(p); await _db.SaveChangesAsync(); return Ok(new { success = true }); }

    // Licenses CRUD
    [HttpGet("licenses")] public async Task<IActionResult> GetLicenses() => Ok(await _db.Licenses.Include("Product").ToListAsync());
    [HttpPost("licenses")] public async Task<IActionResult> CreateLicense([FromBody] License license) { _db.Licenses.Add(license); await _db.SaveChangesAsync(); return Ok(license); }
    [HttpPut("licenses/{id}")] public async Task<IActionResult> UpdateLicense(Guid id, [FromBody] License updated) { var l = await _db.Licenses.FindAsync(id); if (l == null) return NotFound(); l.Edition = updated.Edition; l.ExpireAt = updated.ExpireAt; l.Active = updated.Active; await _db.SaveChangesAsync(); return Ok(l); }
    [HttpDelete("licenses/{id}")] public async Task<IActionResult> DeleteLicense(Guid id) { var l = await _db.Licenses.FindAsync(id); if (l == null) return NotFound(); _db.Licenses.Remove(l); await _db.SaveChangesAsync(); return Ok(new { success = true }); }

    // ActivationCodes CRUD
    [HttpGet("activation-codes")] public async Task<IActionResult> GetActivationCodes() => Ok(await _db.ActivationCodes.ToListAsync());
    [HttpPost("activation-codes")] public async Task<IActionResult> CreateActivationCode([FromBody] ActivationCode code) { _db.ActivationCodes.Add(code); await _db.SaveChangesAsync(); return Ok(code); }
    [HttpPut("activation-codes/{id}")] public async Task<IActionResult> UpdateActivationCode(Guid id, [FromBody] ActivationCode updated) { var c = await _db.ActivationCodes.FindAsync(id); if (c == null) return NotFound(); c.DurationDays = updated.DurationDays; c.MachineLimit = updated.MachineLimit; c.Edition = updated.Edition; await _db.SaveChangesAsync(); return Ok(c); }
    [HttpDelete("activation-codes/{id}")] public async Task<IActionResult> DeleteActivationCode(Guid id) { var c = await _db.ActivationCodes.FindAsync(id); if (c == null) return NotFound(); _db.ActivationCodes.Remove(c); await _db.SaveChangesAsync(); return Ok(new { success = true }); }

    // Machines CRUD
    [HttpGet("machines")] public async Task<IActionResult> GetMachines() => Ok(await _db.Machines.ToListAsync());
    [HttpPost("machines")] public async Task<IActionResult> CreateMachine([FromBody] Machine machine) { _db.Machines.Add(machine); await _db.SaveChangesAsync(); return Ok(machine); }
    [HttpPut("machines/{id}")] public async Task<IActionResult> UpdateMachine(Guid id, [FromBody] Machine updated) { var m = await _db.Machines.FindAsync(id); if (m == null) return NotFound(); m.MachineName = updated.MachineName; await _db.SaveChangesAsync(); return Ok(m); }
    [HttpDelete("machines/{id}")] public async Task<IActionResult> DeleteMachine(Guid id) { var m = await _db.Machines.FindAsync(id); if (m == null) return NotFound(); _db.Machines.Remove(m); await _db.SaveChangesAsync(); return Ok(new { success = true }); }

    // VersionReleases CRUD
    [HttpGet("version-releases")] public async Task<IActionResult> GetVersionReleases() => Ok(await _db.VersionReleases.ToListAsync());
    [HttpPost("version-releases")] public async Task<IActionResult> CreateVersionRelease([FromBody] VersionRelease release) { _db.VersionReleases.Add(release); await _db.SaveChangesAsync(); return Ok(release); }
    [HttpPut("version-releases/{id}")] public async Task<IActionResult> UpdateVersionRelease(Guid id, [FromBody] VersionRelease updated) { var v = await _db.VersionReleases.FindAsync(id); if (v == null) return NotFound(); v.Version = updated.Version; v.Changelog = updated.Changelog; v.DownloadUrl = updated.DownloadUrl; v.ForceUpdate = updated.ForceUpdate; await _db.SaveChangesAsync(); return Ok(v); }
    [HttpDelete("version-releases/{id}")] public async Task<IActionResult> DeleteVersionRelease(Guid id) { var v = await _db.VersionReleases.FindAsync(id); if (v == null) return NotFound(); _db.VersionReleases.Remove(v); await _db.SaveChangesAsync(); return Ok(new { success = true }); }

    // Audit logs
    [HttpGet("audit-logs")] public async Task<IActionResult> GetAuditLogs() => Ok(await _db.AuditLogs.OrderByDescending(a => a.CreatedAt).Take(100).ToListAsync());

    private static bool VerifyPassword(string password, string hash) => hash == $"HASHED:{password}";
}

public class LoginRequest { public string Username { get; set; } = ""; public string Password { get; set; } = ""; }
