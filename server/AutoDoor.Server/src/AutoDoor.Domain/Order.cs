using System;

namespace AutoDoor.Server.Domain;

public class Order
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string OrderNo { get; set; } = "";
    public Guid? UserId { get; set; }
    public Guid? ProductId { get; set; }
    public string Edition { get; set; } = "pro";
    public decimal Amount { get; set; }
    public string PayMethod { get; set; } = "manual";
    public string Status { get; set; } = "pending";
    public string Remark { get; set; } = "";
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime? PaidAt { get; set; }
    public DateTime? RefundedAt { get; set; }
}
