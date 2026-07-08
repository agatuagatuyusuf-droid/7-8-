namespace AutoDoor.CoreService.License;

public enum LicenseState
{
    Unknown,
    NotActivated,
    Active,
    Expired,
    MachineMismatch,
    OfflineExpired,
    InvalidTicket
}
