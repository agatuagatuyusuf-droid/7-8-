using System;
using System.Collections.Generic;
using System.Security.Cryptography;
using System.Text;

namespace AutoDoor.CoreService.Security;

public class LoginSessionService
{
    private const string TestUsername = "admin";

    private const string TestPasswordSha256 =
        "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9";

    private readonly Dictionary<string, LoginSession> _sessions = new();

    public LoginResult Login(string username, string password)
    {
        if (string.IsNullOrWhiteSpace(username) || string.IsNullOrEmpty(password))
        {
            return LoginResult.Fail("用户名或密码为空");
        }

        var passwordHash = Sha256(password);

        if (!string.Equals(username, TestUsername, StringComparison.Ordinal) ||
            !string.Equals(passwordHash, TestPasswordSha256, StringComparison.OrdinalIgnoreCase))
        {
            return LoginResult.Fail("用户名或密码错误");
        }

        var token = "LS-" + Convert.ToHexString(RandomNumberGenerator.GetBytes(32));

        var session = new LoginSession
        {
            Token = token,
            Username = username,
            CreatedAtUtc = DateTime.UtcNow,
            ExpiresAtUtc = DateTime.UtcNow.AddHours(8),
            LastSeenUtc = DateTime.UtcNow
        };

        lock (_sessions)
        {
            _sessions[token] = session;
        }

        return LoginResult.Ok(token, session.ExpiresAtUtc);
    }

    public bool Validate(string token)
    {
        if (string.IsNullOrWhiteSpace(token))
        {
            return false;
        }

        lock (_sessions)
        {
            if (!_sessions.TryGetValue(token, out var session))
            {
                return false;
            }

            if (session.ExpiresAtUtc <= DateTime.UtcNow)
            {
                _sessions.Remove(token);
                return false;
            }

            session.LastSeenUtc = DateTime.UtcNow;
            return true;
        }
    }

    public void Logout(string token)
    {
        if (string.IsNullOrWhiteSpace(token))
        {
            return;
        }

        lock (_sessions)
        {
            _sessions.Remove(token);
        }
    }

    public void ClearAll()
    {
        lock (_sessions)
        {
            _sessions.Clear();
        }
    }

    private static string Sha256(string value)
    {
        var bytes = SHA256.HashData(Encoding.UTF8.GetBytes(value));
        return Convert.ToHexString(bytes).ToLowerInvariant();
    }
}

public class LoginSession
{
    public string Token { get; set; } = "";
    public string Username { get; set; } = "";
    public DateTime CreatedAtUtc { get; set; }
    public DateTime ExpiresAtUtc { get; set; }
    public DateTime LastSeenUtc { get; set; }
}

public class LoginResult
{
    public bool Success { get; set; }
    public string Token { get; set; } = "";
    public string Error { get; set; } = "";
    public DateTime? ExpiresAtUtc { get; set; }

    public static LoginResult Ok(string token, DateTime expiresAtUtc)
    {
        return new LoginResult
        {
            Success = true,
            Token = token,
            ExpiresAtUtc = expiresAtUtc
        };
    }

    public static LoginResult Fail(string error)
    {
        return new LoginResult
        {
            Success = false,
            Error = error
        };
    }
}
