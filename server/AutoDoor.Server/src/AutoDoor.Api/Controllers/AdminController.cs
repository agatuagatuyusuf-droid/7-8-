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
using AutoDoor.Server.Infrastructure.Services;
using AutoDoor.Server.Api.Dtos.Admin;

namespace AutoDoor.Server.Api.Controllers;

[ApiController]
[Route("api/admin")]
[Authorize(Roles = "admin")]
public class AdminController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly IConfiguration _configuration;
    private readonly AdminAuditService _audit;

    public AdminController(AppDbContext db, IConfiguration configuration, AdminAuditService audit)
    {
        _db = db;
        _configuration = configuration;
        _audit = audit;
    }

    private string CurrentAdminId()
    {
        return User.FindFirst(ClaimTypes.NameIdentifier)?.Value ?? "";
    }

    private string ClientIp()
    {
        return HttpContext.Connection.RemoteIpAddress?.ToString() ?? "";
    }

    private string UserAgent()
    {
        return Request.Headers.UserAgent.ToString();
    }

    [AllowAnonymous]
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

        return Ok(new LoginResponse
        {
            Success = true,
            Token = new JwtSecurityTokenHandler().WriteToken(token),
            ExpiresAt = expires.ToString("o")
        });
    }

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

    [HttpGet("users")]
    public async Task<IActionResult> GetUsers(int page = 1, int pageSize = 20)
    {
        var query = _db.Users.AsQueryable();
        var total = await query.CountAsync();
        var items = await query
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .Select(u => new UserDto
            {
                Id = u.Id,
                UserCode = u.UserCode,
                Name = u.Name,
                Email = u.Email
            })
            .ToListAsync();

        return Ok(new { success = true, data = new PagedResult<UserDto> { Page = page, PageSize = pageSize, Total = total, Items = items } });
    }

    [HttpPost("users")]
    public async Task<IActionResult> CreateUser([FromBody] CreateUserRequest request)
    {
        var userCode = $"USER-{Guid.NewGuid().ToString("N")[..8].ToUpperInvariant()}";
        var user = new User { UserCode = userCode, Name = request.Name, Email = request.Email };
        _db.Users.Add(user);
        await _db.SaveChangesAsync();

        await _audit.LogAsync(CurrentAdminId(), "CREATE_USER", "User", user.Id.ToString(), ClientIp(), UserAgent(), new { user.Name, user.Email });

        return Ok(new { success = true, data = new UserDto { Id = user.Id, UserCode = user.UserCode, Name = user.Name, Email = user.Email } });
    }

    [HttpPut("users/{id}")]
    public async Task<IActionResult> UpdateUser(Guid id, [FromBody] UpdateUserRequest request)
    {
        var user = await _db.Users.FindAsync(id);
        if (user == null) return NotFound(new { success = false });

        user.Name = request.Name;
        user.Email = request.Email;
        await _db.SaveChangesAsync();

        await _audit.LogAsync(CurrentAdminId(), "UPDATE_USER", "User", id.ToString(), ClientIp(), UserAgent(), new { request.Name, request.Email });

        return Ok(new { success = true, data = new UserDto { Id = user.Id, UserCode = user.UserCode, Name = user.Name, Email = user.Email } });
    }

    [HttpDelete("users/{id}")]
    public async Task<IActionResult> DeleteUser(Guid id)
    {
        var user = await _db.Users.FindAsync(id);
        if (user == null) return NotFound(new { success = false });
        _db.Users.Remove(user);
        await _db.SaveChangesAsync();

        await _audit.LogAsync(CurrentAdminId(), "DELETE_USER", "User", id.ToString(), ClientIp(), UserAgent(), null);
        return Ok(new { success = true });
    }

    [HttpGet("products")]
    public async Task<IActionResult> GetProducts()
    {
        var items = await _db.Products
            .Select(p => new ProductDto { Id = p.Id, ProductId = p.ProductId, Name = p.Name, Description = p.Description })
            .ToListAsync();
        return Ok(new { success = true, data = items });
    }

    [HttpPost("products")]
    public async Task<IActionResult> CreateProduct([FromBody] CreateProductRequest request)
    {
        var product = new Product { ProductId = request.ProductId, Name = request.Name, Description = request.Description };
        _db.Products.Add(product);
        await _db.SaveChangesAsync();

        await _audit.LogAsync(CurrentAdminId(), "CREATE_PRODUCT", "Product", product.Id.ToString(), ClientIp(), UserAgent(), new { request.ProductId, request.Name });

        return Ok(new { success = true, data = new ProductDto { Id = product.Id, ProductId = product.ProductId, Name = product.Name, Description = product.Description } });
    }

    [HttpPut("products/{id}")]
    public async Task<IActionResult> UpdateProduct(Guid id, [FromBody] UpdateProductRequest request)
    {
        var p = await _db.Products.FindAsync(id);
        if (p == null) return NotFound(new { success = false });
        p.Name = request.Name;
        p.Description = request.Description;
        await _db.SaveChangesAsync();

        await _audit.LogAsync(CurrentAdminId(), "UPDATE_PRODUCT", "Product", id.ToString(), ClientIp(), UserAgent(), new { request.Name });

        return Ok(new { success = true, data = new ProductDto { Id = p.Id, ProductId = p.ProductId, Name = p.Name, Description = p.Description } });
    }

    [HttpDelete("products/{id}")]
    public async Task<IActionResult> DeleteProduct(Guid id)
    {
        var p = await _db.Products.FindAsync(id);
        if (p == null) return NotFound(new { success = false });
        _db.Products.Remove(p);
        await _db.SaveChangesAsync();

        await _audit.LogAsync(CurrentAdminId(), "DELETE_PRODUCT", "Product", id.ToString(), ClientIp(), UserAgent(), null);
        return Ok(new { success = true });
    }

    [HttpGet("licenses")]
    public async Task<IActionResult> GetLicenses(int page = 1, int pageSize = 20)
    {
        var query = _db.Licenses.Include(l => l.Product).AsQueryable();
        var total = await query.CountAsync();
        var items = await query
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .Select(l => new LicenseDto
            {
                Id = l.Id,
                LicenseId = l.LicenseId,
                LicenseType = l.LicenseType,
                Edition = l.Edition,
                ExpireAt = l.ExpireAt,
                Active = l.Active,
                Banned = l.Banned,
                BanReason = l.BanReason,
                MachineLimit = l.MachineLimit,
                OfflineDays = l.OfflineDays
            })
            .ToListAsync();

        return Ok(new { success = true, data = new PagedResult<LicenseDto> { Page = page, PageSize = pageSize, Total = total, Items = items } });
    }

    [HttpPost("licenses/{id}/disable")]
    public async Task<IActionResult> DisableLicense(Guid id)
    {
        var l = await _db.Licenses.FindAsync(id);
        if (l == null) return NotFound(new { success = false });
        l.Active = false;
        await _db.SaveChangesAsync();

        await _audit.LogAsync(CurrentAdminId(), "DISABLE_LICENSE", "License", id.ToString(), ClientIp(), UserAgent(), null);
        return Ok(new { success = true });
    }

    [HttpPost("licenses/{id}/enable")]
    public async Task<IActionResult> EnableLicense(Guid id)
    {
        var l = await _db.Licenses.FindAsync(id);
        if (l == null) return NotFound(new { success = false });
        l.Active = true;
        await _db.SaveChangesAsync();

        await _audit.LogAsync(CurrentAdminId(), "ENABLE_LICENSE", "License", id.ToString(), ClientIp(), UserAgent(), null);
        return Ok(new { success = true });
    }

    [HttpPost("licenses/{id}/extend")]
    public async Task<IActionResult> ExtendLicense(Guid id, [FromBody] ExtendLicenseRequest request)
    {
        if (request.Days <= 0)
            return BadRequest(new { success = false, message = "Days must be greater than 0" });

        var l = await _db.Licenses.FindAsync(id);
        if (l == null) return NotFound(new { success = false });
        l.ExpireAt = l.ExpireAt.AddDays(request.Days);
        await _db.SaveChangesAsync();

        await _audit.LogAsync(CurrentAdminId(), "EXTEND_LICENSE", "License", id.ToString(), ClientIp(), UserAgent(), new { request.Days });
        return Ok(new { success = true, data = new { l.ExpireAt } });
    }

    [HttpPost("activation-codes/generate")]
    public async Task<IActionResult> GenerateActivationCodes([FromBody] GenerateActivationCodesRequest request)
    {
        if (request.Count < 1 || request.Count > 500)
            return BadRequest(new { success = false, message = "Count must be between 1 and 500" });
        if (request.DurationDays <= 0)
            return BadRequest(new { success = false, message = "DurationDays must be greater than 0" });
        if (request.MachineLimit <= 0)
            return BadRequest(new { success = false, message = "MachineLimit must be greater than 0" });

        var product = await _db.Products.FirstOrDefaultAsync(p => p.ProductId == request.ProductId);
        if (product == null)
            return BadRequest(new { success = false, message = $"Product not found: {request.ProductId}" });

        var codes = new List<ActivationCodeDto>();
        for (int i = 0; i < request.Count; i++)
        {
            string code;
            do { code = ActivationCodeGenerator.Generate(); }
            while (await _db.ActivationCodes.AnyAsync(a => a.Code == code));

            var ac = new ActivationCode
            {
                Code = code,
                ProductId = product.Id,
                Edition = request.Edition,
                DurationDays = request.DurationDays,
                MachineLimit = request.MachineLimit,
                CreatedAt = DateTime.UtcNow
            };
            _db.ActivationCodes.Add(ac);
            codes.Add(new ActivationCodeDto
            {
                Id = ac.Id,
                Code = ac.Code,
                Edition = ac.Edition,
                DurationDays = ac.DurationDays,
                MachineLimit = ac.MachineLimit,
                Used = false,
                Disabled = false,
                CreatedAt = ac.CreatedAt
            });
        }

        await _db.SaveChangesAsync();

        await _audit.LogAsync(CurrentAdminId(), "GENERATE_ACTIVATION_CODES", "ActivationCode", $"{request.Count} codes", ClientIp(), UserAgent(), new { request.ProductId, request.Edition, request.DurationDays, request.MachineLimit, Count = request.Count });

        return Ok(new { success = true, data = codes });
    }

    [HttpGet("activation-codes")]
    public async Task<IActionResult> GetActivationCodes(int page = 1, int pageSize = 50)
    {
        var query = _db.ActivationCodes.OrderByDescending(a => a.CreatedAt);
        var total = await query.CountAsync();
        var items = await query
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .Select(a => new ActivationCodeDto
            {
                Id = a.Id,
                Code = a.Code,
                Edition = a.Edition,
                DurationDays = a.DurationDays,
                MachineLimit = a.MachineLimit,
                Used = a.Used,
                Disabled = a.Disabled,
                CreatedAt = a.CreatedAt,
                UsedAt = a.UsedAt
            })
            .ToListAsync();

        return Ok(new { success = true, data = new PagedResult<ActivationCodeDto> { Page = page, PageSize = pageSize, Total = total, Items = items } });
    }

    [HttpGet("machines")]
    public async Task<IActionResult> GetMachines(int page = 1, int pageSize = 50)
    {
        var query = _db.Machines.OrderByDescending(m => m.RegisteredAt);
        var total = await query.CountAsync();
        var items = await query
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .Select(m => new MachineDto
            {
                Id = m.Id,
                MachineCode = m.MachineCode,
                MachineName = m.MachineName,
                Banned = m.Banned,
                BanReason = m.BanReason,
                RegisteredAt = m.RegisteredAt,
                LastHeartbeat = m.LastHeartbeat
            })
            .ToListAsync();

        return Ok(new { success = true, data = new PagedResult<MachineDto> { Page = page, PageSize = pageSize, Total = total, Items = items } });
    }

    [HttpPost("machines/{id}/ban")]
    public async Task<IActionResult> BanMachine(Guid id, [FromBody] BanMachineRequest request)
    {
        var m = await _db.Machines.FindAsync(id);
        if (m == null) return NotFound(new { success = false });
        m.Banned = true;
        m.BanReason = request.Reason;
        await _db.SaveChangesAsync();

        await _audit.LogAsync(CurrentAdminId(), "BAN_MACHINE", "Machine", id.ToString(), ClientIp(), UserAgent(), new { request.Reason });
        return Ok(new { success = true });
    }

    [HttpPost("machines/{id}/unban")]
    public async Task<IActionResult> UnbanMachine(Guid id)
    {
        var m = await _db.Machines.FindAsync(id);
        if (m == null) return NotFound(new { success = false });
        m.Banned = false;
        m.BanReason = "";
        await _db.SaveChangesAsync();

        await _audit.LogAsync(CurrentAdminId(), "UNBAN_MACHINE", "Machine", id.ToString(), ClientIp(), UserAgent(), null);
        return Ok(new { success = true });
    }

    [HttpDelete("machines/{id}")]
    public async Task<IActionResult> DeleteMachine(Guid id)
    {
        var m = await _db.Machines.FindAsync(id);
        if (m == null) return NotFound(new { success = false });
        _db.Machines.Remove(m);
        await _db.SaveChangesAsync();

        await _audit.LogAsync(CurrentAdminId(), "DELETE_MACHINE", "Machine", id.ToString(), ClientIp(), UserAgent(), null);
        return Ok(new { success = true });
    }

    [HttpGet("version-releases")]
    public async Task<IActionResult> GetVersionReleases()
    {
        var items = await _db.VersionReleases
            .OrderByDescending(v => v.ReleasedAt)
            .Select(v => new VersionReleaseDto
            {
                Id = v.Id,
                Version = v.Version,
                Changelog = v.Changelog,
                DownloadUrl = v.DownloadUrl,
                ForceUpdate = v.ForceUpdate,
                MinSupportedVersion = v.MinSupportedVersion
            })
            .ToListAsync();
        return Ok(new { success = true, data = items });
    }

    [HttpPost("version-releases")]
    public async Task<IActionResult> CreateVersionRelease([FromBody] VersionReleaseDto request)
    {
        var release = new VersionRelease
        {
            Version = request.Version,
            Changelog = request.Changelog,
            DownloadUrl = request.DownloadUrl,
            ForceUpdate = request.ForceUpdate
        };
        if (!string.IsNullOrEmpty(request.MinSupportedVersion))
            release.MinSupportedVersion = request.MinSupportedVersion;
        _db.VersionReleases.Add(release);
        await _db.SaveChangesAsync();

        await _audit.LogAsync(CurrentAdminId(), "CREATE_VERSION_RELEASE", "VersionRelease", release.Id.ToString(), ClientIp(), UserAgent(), new { release.Version });

        return Ok(new { success = true, data = new VersionReleaseDto
        {
            Id = release.Id,
            Version = release.Version,
            Changelog = release.Changelog,
            DownloadUrl = release.DownloadUrl,
            ForceUpdate = release.ForceUpdate,
            MinSupportedVersion = release.MinSupportedVersion
        }});
    }

    [HttpPut("version-releases/{id}")]
    public async Task<IActionResult> UpdateVersionRelease(Guid id, [FromBody] VersionReleaseDto request)
    {
        var v = await _db.VersionReleases.FindAsync(id);
        if (v == null) return NotFound(new { success = false });
        v.Version = request.Version;
        v.Changelog = request.Changelog;
        v.DownloadUrl = request.DownloadUrl;
        v.ForceUpdate = request.ForceUpdate;
        v.MinSupportedVersion = request.MinSupportedVersion;
        await _db.SaveChangesAsync();

        await _audit.LogAsync(CurrentAdminId(), "UPDATE_VERSION_RELEASE", "ClientRelease", id.ToString(), ClientIp(), UserAgent(), new { request.Version });

        return Ok(new { success = true, data = request });
    }

    [HttpDelete("version-releases/{id}")]
    public async Task<IActionResult> DeleteVersionRelease(Guid id)
    {
        var v = await _db.VersionReleases.FindAsync(id);
        if (v == null) return NotFound(new { success = false });
        _db.VersionReleases.Remove(v);
        await _db.SaveChangesAsync();

        await _audit.LogAsync(CurrentAdminId(), "DELETE_VERSION_RELEASE", "ClientRelease", id.ToString(), ClientIp(), UserAgent(), null);
        return Ok(new { success = true });
    }

    [HttpGet("orders")]
    public async Task<IActionResult> GetOrders(int page = 1, int pageSize = 20)
    {
        var query = _db.Orders.OrderByDescending(o => o.CreatedAt);
        var total = await query.CountAsync();
        var items = await query
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .Select(o => new OrderDto
            {
                Id = o.Id,
                OrderNo = o.OrderNo,
                Status = o.Status,
                Amount = o.Amount,
                PayMethod = o.PayMethod,
                CreatedAt = o.CreatedAt
            })
            .ToListAsync();

        return Ok(new { success = true, data = new PagedResult<OrderDto> { Page = page, PageSize = pageSize, Total = total, Items = items } });
    }

    [HttpPost("orders")]
    public async Task<IActionResult> CreateOrder([FromBody] CreateOrderRequest request)
    {
        var user = await _db.Users.FirstOrDefaultAsync(u => u.UserCode == request.UserCode);
        var product = await _db.Products.FirstOrDefaultAsync(p => p.ProductId == request.ProductId);

        var order = new Order
        {
            OrderNo = request.OrderNo,
            UserId = user?.Id,
            ProductId = product?.Id,
            Edition = request.Edition,
            Amount = request.Amount,
            PayMethod = request.PayMethod,
            Remark = request.Remark,
            Status = "paid"
        };
        _db.Orders.Add(order);
        await _db.SaveChangesAsync();

        await _audit.LogAsync(CurrentAdminId(), "CREATE_ORDER", "Order", order.Id.ToString(), ClientIp(), UserAgent(), new { order.OrderNo, order.Amount });

        return Ok(new { success = true, data = new OrderDto
        {
            Id = order.Id,
            OrderNo = order.OrderNo,
            Status = order.Status,
            Amount = order.Amount,
            PayMethod = order.PayMethod,
            CreatedAt = order.CreatedAt
        }});
    }

    [HttpGet("audit-logs")]
    public async Task<IActionResult> GetAuditLogs(int page = 1, int pageSize = 50)
    {
        var query = _db.AuditLogs.OrderByDescending(a => a.CreatedAt);
        var total = await query.CountAsync();
        var items = await query
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .Select(a => new AuditLogDto
            {
                Id = a.Id,
                AdminId = a.AdminId,
                Action = a.Action,
                TargetType = a.TargetType,
                TargetId = a.TargetId,
                Ip = a.Ip,
                UserAgent = a.UserAgent,
                DetailsJson = a.DetailsJson,
                CreatedAt = a.CreatedAt
            })
            .ToListAsync();
        return Ok(new { success = true, data = new PagedResult<AuditLogDto> { Page = page, PageSize = pageSize, Total = total, Items = items } });
    }
}
