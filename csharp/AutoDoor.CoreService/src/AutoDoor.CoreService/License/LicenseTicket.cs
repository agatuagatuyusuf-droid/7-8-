using System;
using System.Collections.Generic;
using System.Text.Json;

namespace AutoDoor.CoreService.License;

public class LicenseTicket
{
    public int TicketVersion { get; set; }
    public string ProductId { get; set; } = "";
    public string LicenseId { get; set; } = "";
    public string UserId { get; set; } = "";
    public string MachineCode { get; set; } = "";
    public string Edition { get; set; } = "";
    public List<string> Features { get; set; } = new();
    public DateTime IssuedAt { get; set; }
    public DateTime ExpireAt { get; set; }
    public DateTime OfflineUntil { get; set; }
    public string? ForceUpdateMinVersion { get; set; }
    public string Signature { get; set; } = "";

    public static LicenseTicket? FromJson(string json)
    {
        try
        {
            var doc = JsonDocument.Parse(json);
            var root = doc.RootElement;
            return new LicenseTicket
            {
                TicketVersion = root.GetProperty("ticket_version").GetInt32(),
                ProductId = root.GetProperty("product_id").GetString() ?? "",
                LicenseId = root.GetProperty("license_id").GetString() ?? "",
                UserId = root.GetProperty("user_id").GetString() ?? "",
                MachineCode = root.GetProperty("machine_code").GetString() ?? "",
                Edition = root.GetProperty("edition").GetString() ?? "",
                Features = GetStringList(root, "features"),
                IssuedAt = DateTime.Parse(root.GetProperty("issued_at").GetString() ?? ""),
                ExpireAt = DateTime.Parse(root.GetProperty("expire_at").GetString() ?? ""),
                OfflineUntil = DateTime.Parse(root.GetProperty("offline_until").GetString() ?? ""),
                ForceUpdateMinVersion = root.GetProperty("force_update_min_version").GetString(),
                Signature = root.GetProperty("signature").GetString() ?? ""
            };
        }
        catch
        {
            return null;
        }
    }

    private static List<string> GetStringList(JsonElement element, string property)
    {
        var result = new List<string>();
        if (element.TryGetProperty(property, out var arr))
        {
            foreach (var item in arr.EnumerateArray())
                result.Add(item.GetString() ?? "");
        }
        return result;
    }
}
