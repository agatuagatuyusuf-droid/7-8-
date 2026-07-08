namespace AutoDoor.CoreService.Common;

public class LicenseOptions
{
    public string ServerUrl { get; set; } = "https://YOUR-DOMAIN.com";
    public string ProductId { get; set; } = "autodoor_pro";
    public string PublicKey { get; set; } = "";

    public string ActivateUrl => ServerUrl.TrimEnd('/') + "/api/client/activate";
    public string RefreshUrl => ServerUrl.TrimEnd('/') + "/api/client/refresh";
    public string StatusUrl => ServerUrl.TrimEnd('/') + "/api/client/status";
    public string DeactivateUrl => ServerUrl.TrimEnd('/') + "/api/client/deactivate";
}
