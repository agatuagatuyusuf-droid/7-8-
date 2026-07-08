using System;
using System.Collections.Generic;
using System.Text.Json;

namespace AutoDoor.CoreService.License;

public class LicenseGuard
{
    private readonly LicenseCache _cache;
    private readonly SignatureVerifier _verifier;
    private readonly MachineCodeProvider _machineCode;
    private JsonDocument? _currentTicket;

    public LicenseGuard(LicenseCache cache, SignatureVerifier verifier, MachineCodeProvider machineCode)
    {
        _cache = cache;
        _verifier = verifier;
        _machineCode = machineCode;
        LoadCached();
    }

    private void LoadCached()
    {
        var cached = _cache.Load();
        if (cached != null)
        {
            try
            {
                var doc = JsonDocument.Parse(cached);
                if (_verifier.Verify(doc.RootElement))
                {
                    _currentTicket = doc;
                }
            }
            catch { }
        }
    }

    public void ReloadFromCache()
    {
        _currentTicket?.Dispose();
        _currentTicket = null;
        LoadCached();
    }

    public void ClearCurrent()
    {
        _currentTicket?.Dispose();
        _currentTicket = null;
    }

    public object GetStatus()
    {
        if (_currentTicket == null)
            return new { activated = false };

        try
        {
            var root = _currentTicket.RootElement;
            var expireAt = root.GetProperty("expire_at").GetString() ?? "";
            var machineCode = root.GetProperty("machine_code").GetString() ?? "";
            var currentMachine = _machineCode.Generate();

            var expired = DateTime.Parse(expireAt) < DateTime.UtcNow;
            var machineMatch = machineCode == currentMachine;

            return new
            {
                activated = true,
                expired,
                machine_match = machineMatch,
                expire_at = expireAt,
                edition = root.GetProperty("edition").GetString(),
                license_id = root.GetProperty("license_id").GetString()
            };
        }
        catch
        {
            return new { activated = false, error = "Invalid ticket data" };
        }
    }

    public object GetStatusDto()
    {
        if (_currentTicket == null)
            return new
            {
                activated = false,
                valid = false,
                expired = false,
                machine_match = false,
                expire_at = (string?)null,
                edition = (string?)null,
                license_id = (string?)null,
                features = new List<string>(),
                error = (string?)null
            };

        try
        {
            var root = _currentTicket.RootElement;
            var expireAtStr = root.GetProperty("expire_at").GetString() ?? "";
            var expireAt = DateTime.Parse(expireAtStr);
            var machineCode = root.GetProperty("machine_code").GetString() ?? "";
            var currentMachine = _machineCode.Generate();
            var expired = expireAt < DateTime.UtcNow;
            var machineMatch = machineCode == currentMachine;
            var signatureValid = _verifier.Verify(root);

            var activated = true;
            var valid = activated && signatureValid && !expired && machineMatch;

            return new
            {
                activated,
                valid,
                expired,
                machine_match = machineMatch,
                expire_at = expireAtStr,
                edition = root.GetProperty("edition").GetString(),
                license_id = root.GetProperty("license_id").GetString(),
                features = GetFeatures(),
                error = (string?)null
            };
        }
        catch (Exception ex)
        {
            return new
            {
                activated = false,
                valid = false,
                expired = false,
                machine_match = false,
                expire_at = (string?)null,
                edition = (string?)null,
                license_id = (string?)null,
                features = new List<string>(),
                error = $"Invalid ticket: {ex.Message}"
            };
        }
    }

    public bool CheckFeature(string feature)
    {
        if (_currentTicket == null) return false;

        try
        {
            var root = _currentTicket.RootElement;
            var expireAt = root.GetProperty("expire_at").GetString() ?? "";
            if (DateTime.Parse(expireAt) < DateTime.UtcNow) return false;

            var machineCode = root.GetProperty("machine_code").GetString() ?? "";
            if (machineCode != _machineCode.Generate()) return false;

            var features = root.GetProperty("features").EnumerateArray();
            foreach (var f in features)
            {
                if (f.GetString() == feature) return true;
            }
        }
        catch { }

        return false;
    }

    public List<string> GetFeatures()
    {
        var result = new List<string>();
        if (_currentTicket == null) return result;

        try
        {
            var root = _currentTicket.RootElement;
            var features = root.GetProperty("features").EnumerateArray();
            foreach (var f in features)
            {
                result.Add(f.GetString() ?? "");
            }
        }
        catch { }

        return result;
    }
}
