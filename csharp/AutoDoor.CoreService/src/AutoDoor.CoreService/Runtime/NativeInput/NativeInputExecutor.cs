using System;
using System.Runtime.InteropServices;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace AutoDoor.CoreService.Runtime.NativeInput;

public class NativeInputExecutor
{
    [DllImport("user32.dll")]
    private static extern bool SetCursorPos(int x, int y);

    [DllImport("user32.dll")]
    private static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, UIntPtr dwExtraInfo);

    private const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
    private const uint MOUSEEVENTF_LEFTUP = 0x0004;
    private const uint MOUSEEVENTF_RIGHTDOWN = 0x0008;
    private const uint MOUSEEVENTF_RIGHTUP = 0x0010;
    private const uint MOUSEEVENTF_MIDDLEDOWN = 0x0020;
    private const uint MOUSEEVENTF_MIDDLEUP = 0x0040;

    public Task<(bool success, string? error, string message)> KeyPressAsync(string key, CancellationToken ct)
    {
        if (ct.IsCancellationRequested)
            return Task.FromResult<(bool, string?, string)>((false, "CANCELLED", "Operation cancelled"));

        if (string.IsNullOrWhiteSpace(key))
            return Task.FromResult<(bool, string?, string)>((false, "MISSING_KEY", "key is required"));

        try
        {
            var sendKeys = NormalizeKey(key);
            SendKeys.SendWait(sendKeys);
            return Task.FromResult<(bool, string?, string)>((true, null, "Key pressed"));
        }
        catch (Exception ex)
        {
            return Task.FromResult<(bool, string?, string)>((false, "KEY_PRESS_FAILED", ex.Message));
        }
    }

    public Task<(bool success, string? error, string message)> TextInputAsync(string text, CancellationToken ct)
    {
        if (ct.IsCancellationRequested)
            return Task.FromResult<(bool, string?, string)>((false, "CANCELLED", "Operation cancelled"));

        if (text == null)
            return Task.FromResult<(bool, string?, string)>((false, "MISSING_TEXT", "text is required"));

        try
        {
            SendKeys.SendWait(EscapeSendKeys(text));
            return Task.FromResult<(bool, string?, string)>((true, null, "Text input completed"));
        }
        catch (Exception ex)
        {
            return Task.FromResult<(bool, string?, string)>((false, "TEXT_INPUT_FAILED", ex.Message));
        }
    }

    public Task<(bool success, string? error, string message)> MouseClickAsync(int x, int y, string button, int count, CancellationToken ct)
    {
        if (ct.IsCancellationRequested)
            return Task.FromResult<(bool, string?, string)>((false, "CANCELLED", "Operation cancelled"));

        if (count <= 0)
            count = 1;

        if (count > 10)
            return Task.FromResult<(bool, string?, string)>((false, "CLICK_COUNT_TOO_LARGE", "click count must be <= 10"));

        button = (button ?? "left").Trim().ToLowerInvariant();

        try
        {
            if (!SetCursorPos(x, y))
                return Task.FromResult<(bool, string?, string)>((false, "SET_CURSOR_FAILED", "SetCursorPos failed"));

            for (var i = 0; i < count; i++)
            {
                ct.ThrowIfCancellationRequested();

                switch (button)
                {
                    case "left":
                        mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, UIntPtr.Zero);
                        mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, UIntPtr.Zero);
                        break;
                    case "right":
                        mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, UIntPtr.Zero);
                        mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, UIntPtr.Zero);
                        break;
                    case "middle":
                        mouse_event(MOUSEEVENTF_MIDDLEDOWN, 0, 0, 0, UIntPtr.Zero);
                        mouse_event(MOUSEEVENTF_MIDDLEUP, 0, 0, 0, UIntPtr.Zero);
                        break;
                    default:
                        return Task.FromResult<(bool, string?, string)>((false, "UNSUPPORTED_BUTTON", $"Unsupported mouse button: {button}"));
                }

                Thread.Sleep(50);
            }

            return Task.FromResult<(bool, string?, string)>((true, null, "Mouse click completed"));
        }
        catch (OperationCanceledException)
        {
            return Task.FromResult<(bool, string?, string)>((false, "CANCELLED", "Operation cancelled"));
        }
        catch (Exception ex)
        {
            return Task.FromResult<(bool, string?, string)>((false, "MOUSE_CLICK_FAILED", ex.Message));
        }
    }

    private static string NormalizeKey(string key)
    {
        var k = key.Trim();

        return k.ToLowerInvariant() switch
        {
            "enter" => "{ENTER}",
            "return" => "{ENTER}",
            "tab" => "{TAB}",
            "esc" => "{ESC}",
            "escape" => "{ESC}",
            "space" => " ",
            "backspace" => "{BACKSPACE}",
            "delete" => "{DELETE}",
            "del" => "{DELETE}",
            "up" => "{UP}",
            "down" => "{DOWN}",
            "left" => "{LEFT}",
            "right" => "{RIGHT}",
            "home" => "{HOME}",
            "end" => "{END}",
            "pageup" => "{PGUP}",
            "pagedown" => "{PGDN}",
            _ when k.Length == 1 => EscapeSendKeys(k),
            _ => throw new ArgumentException($"Unsupported key: {key}")
        };
    }

    private static string EscapeSendKeys(string text)
    {
        return text
            .Replace("+", "{+}")
            .Replace("^", "{^}")
            .Replace("%", "{%}")
            .Replace("~", "{~}")
            .Replace("(", "{(}")
            .Replace(")", "{)}")
            .Replace("[", "{[}")
            .Replace("]", "{]}")
            .Replace("{", "{{}")
            .Replace("}", "{}}");
    }
}
