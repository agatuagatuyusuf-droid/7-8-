using System;
using System.Collections.Generic;
using System.IdentityModel.Tokens.Jwt;
using System.Linq;
using System.Security.Claims;
using System.Text;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.IdentityModel.Tokens;
using AutoDoor.Server.Domain;
using AutoDoor.Server.Infrastructure;

namespace AutoDoor.Server.Api.Controllers;

[ApiController]
[Route("api/admin")]
public class AdminController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly IConfiguration _configuration;

    public AdminController(AppDbContext db, IConfiguration configuration)
    {
        _db = db;
        _configuration = configuration;
    }

    [HttpPost("login")]
    public async Task<IActionResult> Login([FromBody] LoginRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.Username) || string.IsNullOrWhiteSpace(request.Password))
            return BadRequest(new { success = false, message = "Username and password required" });

        var admin = await _db.Admins.FirstOrDefaultAsync(a => a.Username == request.Username);
        if (admin == null || !BCrypt.Net.BCrypt.Verify(request.Password, admin.PasswordHash))
            return Unauthorized(new { success = false, message = "Invalid credentials" });

        var jwtSecret = Environment.GetEnvironmentVariable("AUTODOOR_JWT_SECRET")
            ?? _configuration["Jwt:Secret"]
            ?? "CHANGE_ME_DEV_SECRET_MIN_32_CHARS";

        var jwtIssuer = Environment.GetEnvironmentVariable("AUTODOOR_JWT_ISSUER")
            ?? _configuration["Jwt:Issuer"]
            ?? "AutoDoor.Server";

        var jwtAudience = Environment.GetEnvironmentVariable("AUTODOOR_JWT_AUDIENCE")
            ?? _configuration["Jwt:Audience"]
            ?? "AutoDoor.Admin";

        var claims = new List<Claim>
        {
            new Claim(ClaimTypes.NameIdentifier, admin.Id.ToString()),
            new Claim(ClaimTypes.Name, admin.Username),
            new Claim(ClaimTypes.Role, "admin")
        };

        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtSecret));
        var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);
        var expires = DateTime.UtcNow.AddHours(8);

        var token = new JwtSecurityToken(
            issuer: jwtIssuer,
            audience: jwtAudience,
            claims: claims,
            expires: expires,
            signingCredentials: creds
        );

        return Ok(new
        {
            success = true,
            token = new JwtSecurityTokenHandler().WriteToken(token),
            expires_at = expires.ToString("o")
        });
    }

    [Authorize]
    [HttpGet("dashboard")]
    public async Task<IActionResult> Dashboard()
    {
        return Ok(new
        {
            success = true,
            data = new
            {
                total_licenses = await _db.Licenses.CountAsync(),
                active_licenses = await _db.Licenses.CountAsync(l => l.Active),
                total_users = await _db.Users.CountAsync(),
                total_machines = await _db.Machines.CountAsync()
            }
        });
    }

    [Authorize]
    [HttpGet("users")]
    public async Task<IActionResult> GetUsers() => Ok(new { success = true, data = await _db.Users.ToListAsync() });

    [Authorize]
    [HttpPost("users")]
    public async Task<IActionResult> CreateUser([FromBody] User user) { _db.Users.Add(user); await _db.SaveChangesAsync(); return Ok(new { success = true, data = user }); }

    [Authorize]
    [HttpPut("users/{id}")]
    public async Task<IActionResult> UpdateUser(Guid id, [FromBody] User updated) { var user = await _db.Users.FindAsync(id); if (user == null) return NotFound(new { success = false }); user.Name = updated.Name; user.Email = updated.Email; await _db.SaveChangesAsync(); return Ok(new { success = true, data = user }); }

    [Authorize]
    [HttpDelete("users/{id}")]
    public async Task<IActionResult> DeleteUser(Guid id) { var user = await _db.Users.FindAsync(id); if (user == null) return NotFound(new { success = false }); _db.Users.Remove(user); await _db.SaveChangesAsync(); return Ok(new { success = true }); }

    [Authorize]
    [HttpGet("products")]
    public async Task<IActionResult> GetProducts() => Ok(new { success = true, data = await _db.Products.ToListAsync() });

    [Authorize]
    [HttpPost("products")]
    public async Task<IActionResult> CreateProduct([FromBody] Product product) { _db.Products.Add(product); await _db.SaveChangesAsync(); return Ok(new { success = true, data = product }); }

    [Authorize]
    [HttpPut("products/{id}")]
    public async Task<IActionResult> UpdateProduct(Guid id, [FromBody] Product updated) { var p = await _db.Products.FindAsync(id); if (p == null) return NotFound(new { success = false }); p.Name = updated.Name; p.Description = updated.Description; await _db.SaveChangesAsync(); return Ok(new { success = true, data = p }); }

    [Authorize]
    [HttpDelete("products/{id}")]
    public async Task<IActionResult> DeleteProduct(Guid id) { var p = await _db.Products.FindAsync(id); if (p == null) return NotFound(new { success = false }); _db.Products.Remove(p); await _db.SaveChangesAsync(); return Ok(new { success = true }); }

    [Authorize]
    [HttpGet("licenses")]
    public async Task<IActionResult> GetLicenses() => Ok(new { success = true, data = await _db.Licenses.Include(l => l.Product).ToListAsync() });

    [Authorize]
    [HttpPost("licenses")]
    public async Task<IActionResult> CreateLicense([FromBody] License license) { _db.Licenses.Add(license); await _db.SaveChangesAsync(); return Ok(new { success = true, data = license }); }

    [Authorize]
    [HttpPut("licenses/{id}")]
    public async Task<IActionResult> UpdateLicense(Guid id, [FromBody] License updated) { var l = await _db.Licenses.FindAsync(id); if (l == null) return NotFound(new { success = false }); l.Edition = updated.Edition; l.ExpireAt = updated.ExpireAt; l.Active = updated.Active; await _db.SaveChangesAsync(); return Ok(new { success = true, data = l }); }

    [Authorize]
    [HttpDelete("licenses/{id}")]
    public async Task<IActionResult> DeleteLicense(Guid id) { var l = await _db.Licenses.FindAsync(id); if (l == null) return NotFound(new { success = false }); _db.Licenses.Remove(l); await _db.SaveChangesAsync(); return Ok(new { success = true }); }

    [Authorize]
    [HttpGet("activation-codes")]
    public async Task<IActionResult> GetActivationCodes() => Ok(new { success = true, data = await _db.ActivationCodes.ToListAsync() });

    [Authorize]
    [HttpPost("activation-codes")]
    public async Task<IActionResult> CreateActivationCode([FromBody] ActivationCode code) { _db.ActivationCodes.Add(code); await _db.SaveChangesAsync(); return Ok(new { success = true, data = code }); }

    [Authorize]
    [HttpPut("activation-codes/{id}")]
    public async Task<IActionResult> UpdateActivationCode(Guid id, [FromBody] ActivationCode updated) { var c = await _db.ActivationCodes.FindAsync(id); if (c == null) return NotFound(new { success = false }); c.DurationDays = updated.DurationDays; c.MachineLimit = updated.MachineLimit; c.Edition = updated.Edition; await _db.SaveChangesAsync(); return Ok(new { success = true, data = c }); }

    [Authorize]
    [HttpDelete("activation-codes/{id}")]
    public async Task<IActionResult> DeleteActivationCode(Guid id) { var c = await _db.ActivationCodes.FindAsync(id); if (c == null) return NotFound(new { success = false }); _db.ActivationCodes.Remove(c); await _db.SaveChangesAsync(); return Ok(new { success = true }); }

    [Authorize]
    [HttpGet("machines")]
    public async Task<IActionResult> GetMachines() => Ok(new { success = true, data = await _db.Machines.ToListAsync() });

    [Authorize]
    [HttpPut("machines/{id}")]
    public async Task<IActionResult> UpdateMachine(Guid id, [FromBody] Machine updated) { var m = await _db.Machines.FindAsync(id); if (m == null) return NotFound(new { success = false }); m.MachineName = updated.MachineName; await _db.SaveChangesAsync(); return Ok(new { success = true, data = m }); }

    [Authorize]
    [HttpDelete("machines/{id}")]
    public async Task<IActionResult> DeleteMachine(Guid id) { var m = await _db.Machines.FindAsync(id); if (m == null) return NotFound(new { success = false }); _db.Machines.Remove(m); await _db.SaveChangesAsync(); return Ok(new { success = true }); }

    [Authorize]
    [HttpGet("version-releases")]
    public async Task<IActionResult> GetVersionReleases() => Ok(new { success = true, data = await _db.VersionReleases.ToListAsync() });

    [Authorize]
    [HttpPost("version-releases")]
    public async Task<IActionResult> CreateVersionRelease([FromBody] VersionRelease release) { _db.VersionReleases.Add(release); await _db.SaveChangesAsync(); return Ok(new { success = true, data = release }); }

    [Authorize]
    [HttpPut("version-releases/{id}")]
    public async Task<IActionResult> UpdateVersionRelease(Guid id, [FromBody] VersionRelease updated) { var v = await _db.VersionReleases.FindAsync(id); if (v == null) return NotFound(new { success = false }); v.Version = updated.Version; v.Changelog = updated.Changelog; v.DownloadUrl = updated.DownloadUrl; v.ForceUpdate = updated.ForceUpdate; await _db.SaveChangesAsync(); return Ok(new { success = true, data = v }); }

    [Authorize]
    [HttpDelete("version-releases/{id}")]
    public async Task<IActionResult> DeleteVersionRelease(Guid id) { var v = await _db.VersionReleases.FindAsync(id); if (v == null) return NotFound(new { success = false }); _db.VersionReleases.Remove(v); await _db.SaveChangesAsync(); return Ok(new { success = true }); }

    [Authorize]
    [HttpGet("audit-logs")]
    public async Task<IActionResult> GetAuditLogs() => Ok(new { success = true, data = await _db.AuditLogs.OrderByDescending(a => a.CreatedAt).Take(100).ToListAsync() });
}

public class LoginRequest { public string Username { get; set; } = ""; public string Password { get; set; } = ""; }