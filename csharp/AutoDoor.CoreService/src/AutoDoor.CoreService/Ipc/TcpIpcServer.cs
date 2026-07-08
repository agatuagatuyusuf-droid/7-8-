using System;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using AutoDoor.CoreService.Common;
using AutoDoor.CoreService.License;
using AutoDoor.CoreService.Runtime;
using AutoDoor.CoreService.BehaviorTree;

namespace AutoDoor.CoreService.Ipc;

public class TcpIpcServer
{
    private readonly LicenseGuard _licenseGuard;
    private readonly LicenseClient _licenseClient;
    private readonly MachineCodeProvider _machineCodeProvider;
    private readonly FeatureGate _featureGate;
    private readonly RuntimeHost _runtimeHost;
    private readonly IpcSettings _settings;
    private TcpListener? _listener;
    private bool _running;
    private readonly SemaphoreSlim _concurrencySemaphore;

    public TcpIpcServer(
        LicenseGuard licenseGuard,
        LicenseClient licenseClient,
        MachineCodeProvider machineCodeProvider,
        FeatureGate featureGate,
        RuntimeHost runtimeHost,
        AppSettings appSettings)
    {
        _licenseGuard = licenseGuard;
        _licenseClient = licenseClient;
        _machineCodeProvider = machineCodeProvider;
        _featureGate = featureGate;
        _runtimeHost = runtimeHost;
        _settings = appSettings.Ipc;
        _concurrencySemaphore = new SemaphoreSlim(_settings.MaxConcurrentRequests);
    }

    public async Task StartAsync(CancellationToken ct)
    {
        _running = true;
        _listener = new TcpListener(IPAddress.Parse(_settings.Host), _settings.Port);
        _listener.Start();

        Console.WriteLine($"TCP IPC listening on {_settings.Host}:{_settings.Port}");

        while (!ct.IsCancellationRequested)
        {
            try
            {
                var client = await _listener.AcceptTcpClientAsync(ct);
                _ = Task.Run(() => HandleClientAsync(client, ct), ct);
            }
            catch (OperationCanceledException)
            {
                break;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"Accept error: {ex.Message}");
            }
        }
    }

    public void Stop()
    {
        _running = false;
        _listener?.Stop();
    }

    private async Task HandleClientAsync(TcpClient tcpClient, CancellationToken ct)
    {
        await _concurrencySemaphore.WaitAsync(ct);
        try
        {
            using (tcpClient)
            using (var stream = tcpClient.GetStream())
            using (var reader = new StreamReader(stream, Encoding.UTF8))
            using (var writer = new StreamWriter(stream, new UTF8Encoding(false)) { AutoFlush = true, NewLine = "\n" })
            {
                string? line;
                while ((line = await reader.ReadLineAsync(ct)) != null)
                {
                    var response = await ProcessMessageAsync(line);
                    await writer.WriteLineAsync(response);
                }
            }
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"TCP client error: {ex.Message}");
        }
        finally
        {
            _concurrencySemaphore.Release();
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
            var id = root.GetProperty("id").GetString() ?? Guid.NewGuid().ToString();

            if (type == "request")
            {
                var payload = root.TryGetProperty("payload", out var p) ? p : default;
                var result = await DispatchActionAsync(action, payload);
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
                error_code = "UNKNOWN_TYPE",
                message = $"Unknown message type: {type}"
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
            "tree.validate" => HandleTreeValidate(payload),
            "tree.start" => await HandleTreeStartAsync(payload),
            "tree.pause" => HandleTreePause(),
            "tree.resume" => HandleTreeResume(),
            "tree.stop" => HandleTreeStop(),
            "tree.status" => HandleTreeStatus(),
            "runtime.logs" => HandleRuntimeLogs(),
            "runtime.stats" => HandleRuntimeStats(),
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
        var code = _machineCodeProvider.Generate();
        return (true, null, "OK", new { machine_code = code });
    }

    private (bool, string?, string, object?) HandleLicenseStatus()
    {
        var status = _licenseGuard.GetStatusDto();
        return (true, null, "OK", status);
    }

    private async Task<(bool, string?, string, object?)> HandleLicenseActivateAsync(JsonElement payload)
    {
        if (payload.ValueKind != JsonValueKind.Object || !payload.TryGetProperty("code", out var codeProp))
            return (false, "MISSING_CODE", "Activation code is required", null);

        var code = codeProp.GetString() ?? "";
        var result = await _licenseClient.ActivateAsync(code);
        if (result.success)
        {
            _licenseGuard.ReloadFromCache();
        }
        return (result.success, result.errorCode, result.message, result.data);
    }

    private async Task<(bool, string?, string, object?)> HandleLicenseRefreshAsync()
    {
        var result = await _licenseClient.RefreshAsync();
        if (result.success)
        {
            _licenseGuard.ReloadFromCache();
        }
        return (result.success, result.errorCode, result.message, result.data);
    }

    private async Task<(bool, string?, string, object?)> HandleLicenseDeactivateAsync()
    {
        var result = await _licenseClient.DeactivateAsync();
        _licenseGuard.ClearCurrent();
        return (result.success, result.errorCode, result.message, result.data);
    }

    private (bool, string?, string, object?) HandleFeatureCheck(JsonElement payload)
    {
        if (payload.ValueKind != JsonValueKind.Object || !payload.TryGetProperty("feature", out var featureProp))
            return (false, "MISSING_FEATURE", "Feature name is required", null);

        var feature = featureProp.GetString() ?? "";
        var allowed = _featureGate.IsEnabled(feature);
        return (true, null, "OK", new { feature, allowed });
    }

    private (bool, string?, string, object?) HandleFeatureList()
    {
        var features = _licenseGuard.GetFeatures();
        return (true, null, "OK", new { features });
    }

    private (bool, string?, string, object?) HandleTreeValidate(JsonElement payload)
    {
        try
        {
            if (payload.ValueKind != JsonValueKind.Object || !payload.TryGetProperty("tree", out var treeElement))
                return (false, "MISSING_TREE", "Tree data is required", null);

            var tree = TreeSerializer.Deserialize(treeElement);
            return (true, null, "Tree validation successful", new { valid = true, node_count = CountNodes(tree) });
        }
        catch (NotImplementedException ex)
        {
            return (true, null, ex.Message, new { valid = false, error = ex.Message });
        }
        catch (Exception ex)
        {
            return (false, "TREE_PARSE_ERROR", $"Tree parse error: {ex.Message}", null);
        }
    }

    private Task<(bool, string?, string, object?)> HandleTreeStartAsync(JsonElement payload)
    {
        try
        {
            if (payload.ValueKind != JsonValueKind.Object || !payload.TryGetProperty("tree", out var treeElement))
                return Task.FromResult<(bool, string?, string, object?)>((false, "MISSING_TREE", "Tree data is required", null));

            var tree = TreeSerializer.Deserialize(treeElement);
            var result = _runtimeHost.StartTree(tree);
            return Task.FromResult<(bool, string?, string, object?)>((result.success, result.error, result.message, null));
        }
        catch (NotImplementedException ex)
        {
            return Task.FromResult<(bool, string?, string, object?)>((false, "NODE_NOT_IMPLEMENTED", ex.Message, null));
        }
        catch (Exception ex)
        {
            return Task.FromResult<(bool, string?, string, object?)>((false, "TREE_START_ERROR", $"Tree start error: {ex.Message}", null));
        }
    }

    private (bool, string?, string, object?) HandleTreePause()
    {
        var result = _runtimeHost.Pause();
        return (result.success, result.error, result.message, null);
    }

    private (bool, string?, string, object?) HandleTreeResume()
    {
        var result = _runtimeHost.Resume();
        return (result.success, result.error, result.message, null);
    }

    private (bool, string?, string, object?) HandleTreeStop()
    {
        var result = _runtimeHost.Stop();
        return (result.success, result.error, result.message, null);
    }

    private (bool, string?, string, object?) HandleTreeStatus()
    {
        return (true, null, "OK", _runtimeHost.Status());
    }

    private (bool, string?, string, object?) HandleRuntimeLogs()
    {
        return (true, null, "OK", _runtimeHost.Logs());
    }

    private (bool, string?, string, object?) HandleRuntimeStats()
    {
        return (true, null, "OK", _runtimeHost.Stats());
    }

    private static int CountNodes(NodeBase node)
    {
        int count = 1;
        foreach (var child in node.Children)
            count += CountNodes(child);
        return count;
    }
}
