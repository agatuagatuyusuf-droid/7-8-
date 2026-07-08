using System;
using System.IO;
using System.IO.Pipes;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using System.Collections.Concurrent;
using AutoDoor.CoreService.License;

namespace AutoDoor.CoreService.Ipc;

public class IpcServer
{
    private readonly string _pipeName;
    private readonly LicenseGuard _licenseGuard;
    private readonly LicenseClient _licenseClient;
    private bool _running;

    public IpcServer(LicenseGuard licenseGuard, LicenseClient licenseClient)
    {
        _pipeName = "AutoDoorPro.CoreService";
        _licenseGuard = licenseGuard;
        _licenseClient = licenseClient;
    }

    public async Task StartAsync(CancellationToken ct)
    {
        _running = true;

        while (_running && !ct.IsCancellationRequested)
        {
            var serverStream = new NamedPipeServerStream(
                _pipeName,
                PipeDirection.InOut,
                NamedPipeServerStream.MaxAllowedServerInstances,
                PipeTransmissionMode.Message,
                PipeOptions.Asynchronous);

            await serverStream.WaitForConnectionAsync(ct);

            _ = Task.Run(() => HandleClientAsync(serverStream, ct), ct);
        }
    }

    public void Stop()
    {
        _running = false;
    }

    private async Task HandleClientAsync(NamedPipeServerStream stream, CancellationToken ct)
    {
        try
        {
            using var reader = new StreamReader(stream, Encoding.UTF8);
            using var writer = new StreamWriter(stream, Encoding.UTF8)
            {
                AutoFlush = true
            };

            string? line;
            while ((line = await reader.ReadLineAsync(ct)) != null)
            {
                var response = await ProcessMessageAsync(line);
                await writer.WriteLineAsync(response);
            }
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"IPC client error: {ex.Message}");
        }
        finally
        {
            stream.Dispose();
        }
    }

    private async Task<string> ProcessMessageAsync(string messageJson)
    {
        try
        {
            using var doc = JsonDocument.Parse(messageJson);
            var root = doc.RootElement;

            var type = root.GetProperty("type").GetString();
            var action = root.GetProperty("action").GetString();
            var id = root.GetProperty("id").GetString();

            if (type == "request")
            {
                var result = await DispatchActionAsync(action, root.TryGetProperty("payload", out var p) ? p : default);
                return JsonSerializer.Serialize(new
                {
                    id,
                    type = "response",
                    success = result.success,
                    error_code = result.errorCode,
                    message = result.message,
                    data = result.data
                });
            }

            return JsonSerializer.Serialize(new
            {
                id,
                type = "response",
                success = false,
                error_code = "UNKNOWN_ACTION",
                message = $"Unknown action: {action}"
            });
        }
        catch (JsonException ex)
        {
            return JsonSerializer.Serialize(new
            {
                id = "",
                type = "response",
                success = false,
                error_code = "INVALID_JSON",
                message = ex.Message
            });
        }
    }

    private async Task<(bool success, string? errorCode, string message, object? data)> DispatchActionAsync(
        string? action, JsonElement payload)
    {
        return action switch
        {
            "core.hello" => (true, null, "OK", new { status = "running" }),
            "core.shutdown" => await HandleShutdownAsync(),
            "license.machine_code" => HandleMachineCode(),
            "license.status" => HandleLicenseStatus(),
            "license.activate" => await HandleLicenseActivateAsync(payload),
            "license.refresh" => await HandleLicenseRefreshAsync(),
            "license.deactivate" => await HandleLicenseDeactivateAsync(),
            "feature.check" => HandleFeatureCheck(payload),
            "feature.list" => HandleFeatureList(),
            _ => (false, "UNKNOWN_ACTION", $"Unknown action: {action}", null)
        };
    }

    private async Task<(bool, string?, string, object?)> HandleShutdownAsync()
    {
        await Task.Run(() => Stop());
        return (true, null, "Shutting down", null);
    }

    private (bool, string?, string, object?) HandleMachineCode()
    {
        var provider = new MachineCodeProvider();
        var code = provider.Generate();
        return (true, null, "OK", new { machine_code = code });
    }

    private (bool, string?, string, object?) HandleLicenseStatus()
    {
        var status = _licenseGuard.GetStatus();
        return (true, null, "OK", status);
    }

    private async Task<(bool, string?, string, object?)> HandleLicenseActivateAsync(JsonElement payload)
    {
        if (!payload.TryGetProperty("code", out var codeProp))
            return (false, "MISSING_CODE", "Activation code is required", null);

        var code = codeProp.GetString() ?? "";
        var result = await _licenseClient.ActivateAsync(code);
        return result;
    }

    private async Task<(bool, string?, string, object?)> HandleLicenseRefreshAsync()
    {
        var result = await _licenseClient.RefreshAsync();
        return result;
    }

    private async Task<(bool, string?, string, object?)> HandleLicenseDeactivateAsync()
    {
        var result = await _licenseClient.DeactivateAsync();
        return result;
    }

    private (bool, string?, string, object?) HandleFeatureCheck(JsonElement payload)
    {
        if (!payload.TryGetProperty("feature", out var featureProp))
            return (false, "MISSING_FEATURE", "Feature name is required", null);

        var feature = featureProp.GetString() ?? "";
        var allowed = _licenseGuard.CheckFeature(feature);
        return (true, null, "OK", new { feature, allowed });
    }

    private (bool, string?, string, object?) HandleFeatureList()
    {
        var features = _licenseGuard.GetFeatures();
        return (true, null, "OK", new { features });
    }
}

internal static class JsonExtensions
{
    public static bool TryGetProperty(this JsonElement element, string propertyName, out JsonElement value)
    {
        value = default;
        if (element.ValueKind != JsonValueKind.Object) return false;
        return element.TryGetProperty(propertyName, out value);
    }
}
