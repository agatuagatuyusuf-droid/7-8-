using System;
using System.Threading.Tasks;
using System.Text.Json;
using AutoDoor.Server.Domain;

namespace AutoDoor.Server.Infrastructure.Services;

public class AdminAuditService
{
    private readonly AppDbContext _db;

    public AdminAuditService(AppDbContext db)
    {
        _db = db;
    }

    public async Task LogAsync(
        string adminId,
        string action,
        string targetType,
        string targetId,
        string ip,
        string userAgent,
        object? details = null)
    {
        var log = new AuditLog
        {
            AdminId = adminId,
            Action = action,
            TargetType = targetType,
            TargetId = targetId,
            Ip = ip,
            UserAgent = userAgent,
            DetailsJson = details == null ? "" : JsonSerializer.Serialize(details),
            CreatedAt = DateTime.UtcNow
        };

        _db.AuditLogs.Add(log);
        await _db.SaveChangesAsync();
    }
}
