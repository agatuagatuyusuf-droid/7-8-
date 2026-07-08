using System;

namespace AutoDoor.CoreService.License;

public class FeatureGate
{
    private readonly LicenseGuard _licenseGuard;

    public FeatureGate(LicenseGuard licenseGuard)
    {
        _licenseGuard = licenseGuard;
    }

    public void Require(string feature)
    {
        if (!_licenseGuard.CheckFeature(feature))
            throw new UnauthorizedFeatureException(feature);
    }

    public bool IsEnabled(string feature)
    {
        return _licenseGuard.CheckFeature(feature);
    }
}

public class UnauthorizedFeatureException : Exception
{
    public string Feature { get; }

    public UnauthorizedFeatureException(string feature)
        : base($"Feature '{feature}' is not authorized in current license")
    {
        Feature = feature;
    }
}
