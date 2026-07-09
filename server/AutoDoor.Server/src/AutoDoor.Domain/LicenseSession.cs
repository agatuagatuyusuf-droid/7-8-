using System;

namespace AutoDoor.Server.Domain;

public class LicenseSession
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string SessionId { get; set; } = "";
    public Guid LicenseId { get; set; }
    public string MachineCode { get; set; } = "";
    public string Ip { get; set; } = "";
    public string AppVersion { get; set; } = "";
    public string CoreVersion { get; set; } = "";
    public bool Active { get; set; } = true;
    public DateTime StartedAt { get; set; } = DateTime.UtcNow;
    public DateTime LastSeenAt { get; set; } = DateTime.UtcNow;
}
