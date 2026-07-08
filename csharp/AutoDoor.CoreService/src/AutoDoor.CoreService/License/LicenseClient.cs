using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using AutoDoor.CoreService.Common;

namespace AutoDoor.CoreService.License;

public class LicenseClient
{
    private readonly HttpClient _httpClient;
    private readonly MachineCodeProvider _machineCode;
    private readonly LicenseCache _cache;
    private readonly SignatureVerifier _verifier;
    private readonly LicenseOptions _options;

    public LicenseClient(MachineCodeProvider machineCode, LicenseCache cache, SignatureVerifier verifier, AppSettings appSettings)
    {
        _httpClient = new HttpClient();
        _machineCode = machineCode;
        _cache = cache;
        _verifier = verifier;

        var envUrl = Environment.GetEnvironmentVariable("AUTODOOR_LICENSE_SERVER_URL");
        var envProductId = Environment.GetEnvironmentVariable("AUTODOOR_PRODUCT_ID");
        _options = new LicenseOptions
        {
            ServerUrl = envUrl ?? appSettings.License.ServerUrl,
            ProductId = envProductId ?? appSettings.License.ProductId,
            PublicKey = appSettings.License.PublicKey
        };
    }

    public async Task<(bool success, string? errorCode, string message, object? data)> ActivateAsync(string code)
    {
        try
        {
            var machineCode = _machineCode.Generate();
            var payload = new
            {
                activation_code = code,
                machine_code = machineCode,
                product_id = _options.ProductId
            };

            var json = JsonSerializer.Serialize(payload);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync(_options.ActivateUrl, content);

            if (!response.IsSuccessStatusCode)
                return (false, "ACTIVATE_FAILED", "Server returned error", null);

            var responseJson = await response.Content.ReadAsStringAsync();
            var result = JsonSerializer.Deserialize<JsonElement>(responseJson);

            if (result.TryGetProperty("ticket", out var ticket))
            {
                var verified = _verifier.Verify(ticket);
                if (!verified)
                    return (false, "INVALID_TICKET", "License ticket signature invalid", null);

                var ticketStr = ticket.GetRawText();
                _cache.Save(ticketStr);
                return (true, null, "Activation successful", new { ticket = ticketStr });
            }

            return (false, "NO_TICKET", "No ticket in response", null);
        }
        catch (HttpRequestException ex)
        {
            return (false, "NETWORK_ERROR", $"Network error: {ex.Message}", null);
        }
        catch (Exception ex)
        {
            return (false, "ACTIVATE_ERROR", $"Activation error: {ex.Message}", null);
        }
    }

    public async Task<(bool success, string? errorCode, string message, object? data)> RefreshAsync()
    {
        var cached = _cache.Load();
        if (cached == null)
            return (false, "NO_CACHE", "No license cache", null);

        try
        {
            var machineCode = _machineCode.Generate();
            var payload = new
            {
                machine_code = machineCode,
                product_id = _options.ProductId
            };

            var json = JsonSerializer.Serialize(payload);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync(_options.RefreshUrl, content);

            if (response.IsSuccessStatusCode)
            {
                var responseJson = await response.Content.ReadAsStringAsync();
                var result = JsonSerializer.Deserialize<JsonElement>(responseJson);

                if (result.TryGetProperty("ticket", out var ticket))
                {
                    var verified = _verifier.Verify(ticket);
                    if (verified)
                    {
                        _cache.Save(ticket.GetRawText());
                        return (true, null, "Refresh successful", null);
                    }
                }
            }

            var cachedData = _cache.Load();
            if (cachedData != null && _cache.IsWithinOfflinePeriod(cachedData))
                return (true, null, "Using cached license (offline)", cachedData);

            return (false, "OFFLINE_EXPIRED", "Offline period expired", null);
        }
        catch (HttpRequestException)
        {
            var cachedData = _cache.Load();
            if (cachedData != null && _cache.IsWithinOfflinePeriod(cachedData))
                return (true, null, "Using cached license (offline)", cachedData);

            return (false, "OFFLINE_EXPIRED", "Offline period expired", null);
        }
    }

    public async Task<(bool success, string? errorCode, string message, object? data)> DeactivateAsync()
    {
        _cache.Clear();
        return (true, null, "Deactivated", null);
    }
}
