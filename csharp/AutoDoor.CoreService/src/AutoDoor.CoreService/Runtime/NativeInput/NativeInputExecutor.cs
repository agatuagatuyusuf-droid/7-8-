using System;
using System.Runtime.InteropServices;
using System.Threading;
using System.Threading.Tasks;

namespace AutoDoor.CoreService.Runtime.NativeInput;

public class NativeInputExecutor
{
    private const int INPUT_MOUSE = 0;
    private const int INPUT_KEYBOARD = 1;

    private const uint KEYEVENTF_KEYUP = 0x0002;
    private const uint KEYEVENTF_UNICODE = 0x0004;

    private const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
    private const uint MOUSEEVENTF_LEFTUP = 0x0004;
    private const uint MOUSEEVENTF_RIGHTDOWN = 0x0008;
    private const uint MOUSEEVENTF_RIGHTUP = 0x0010;
    private const uint MOUSEEVENTF_MIDDLEDOWN = 0x0020;
    private const uint MOUSEEVENTF_MIDDLEUP = 0x0040;

    [DllImport("user32.dll")]
    private static extern bool SetCursorPos(int x, int y);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);

    [StructLayout(LayoutKind.Sequential)]
    private struct INPUT
    {
        public int type;
        public InputUnion U;
    }

    [StructLayout(LayoutKind.Explicit)]
    private struct InputUnion
    {
        [FieldOffset(0)]
        public MOUSEINPUT mi;

        [FieldOffset(0)]
        public KEYBDINPUT ki;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct MOUSEINPUT
    {
        public int dx;
        public int dy;
        public uint mouseData;
        public uint dwFlags;
        public uint time;
        public UIntPtr dwExtraInfo;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct KEYBDINPUT
    {
        public ushort wVk;
        public ushort wScan;
        public uint dwFlags;
        public uint time;
        public UIntPtr dwExtraInfo;
    }

    public Task<(bool success, string? error, string message)> KeyPressAsync(string key, CancellationToken ct)
    {
        if (ct.IsCancellationRequested)
            return Task.FromResult<(bool, string?, string)>((false, "CANCELLED", "Operation cancelled"));

        if (string.IsNullOrWhiteSpace(key))
            return Task.FromResult<(bool, string?, string)>((false, "MISSING_KEY", "key is required"));

        try
        {
            var vk = NormalizeVirtualKey(key);
            SendVirtualKey(vk, ct);
            return Task.FromResult<(bool, string?, string)>((true, null, "Key pressed"));
        }
        catch (OperationCanceledException)
        {
            return Task.FromResult<(bool, string?, string)>((false, "CANCELLED", "Operation cancelled"));
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

        if (text.Length > 2000)
            return Task.FromResult<(bool, string?, string)>((false, "TEXT_TOO_LONG", "text length must be <= 2000"));

        try
        {
            foreach (var ch in text)
            {
                ct.ThrowIfCancellationRequested();
                SendUnicodeChar(ch);
            }

            return Task.FromResult<(bool, string?, string)>((true, null, "Text input completed"));
        }
        catch (OperationCanceledException)
        {
            return Task.FromResult<(bool, string?, string)>((false, "CANCELLED", "Operation cancelled"));
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
                        SendMouseButton(MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP);
                        break;
                    case "right":
                        SendMouseButton(MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP);
                        break;
                    case "middle":
                        SendMouseButton(MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP);
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

    private static ushort NormalizeVirtualKey(string key)
    {
        var k = key.Trim();

        if (k.Length == 1)
        {
            var upper = char.ToUpperInvariant(k[0]);
            if (upper >= 'A' && upper <= 'Z')
                return upper;

            if (upper >= '0' && upper <= '9')
                return upper;

            if (upper == ' ')
                return 0x20;
        }

        return k.ToLowerInvariant() switch
        {
            "enter" => 0x0D,
            "return" => 0x0D,
            "tab" => 0x09,
            "esc" => 0x1B,
            "escape" => 0x1B,
            "space" => 0x20,
            "backspace" => 0x08,
            "delete" => 0x2E,
            "del" => 0x2E,
            "up" => 0x26,
            "down" => 0x28,
            "left" => 0x25,
            "right" => 0x27,
            "home" => 0x24,
            "end" => 0x23,
            "pageup" => 0x21,
            "pagedown" => 0x22,
            _ => throw new ArgumentException($"Unsupported key: {key}")
        };
    }

    private static void SendVirtualKey(ushort virtualKey, CancellationToken ct)
    {
        ct.ThrowIfCancellationRequested();

        var inputs = new[]
        {
            new INPUT
            {
                type = INPUT_KEYBOARD,
                U = new InputUnion
                {
                    ki = new KEYBDINPUT
                    {
                        wVk = virtualKey,
                        wScan = 0,
                        dwFlags = 0,
                        time = 0,
                        dwExtraInfo = UIntPtr.Zero
                    }
                }
            },
            new INPUT
            {
                type = INPUT_KEYBOARD,
                U = new InputUnion
                {
                    ki = new KEYBDINPUT
                    {
                        wVk = virtualKey,
                        wScan = 0,
                        dwFlags = KEYEVENTF_KEYUP,
                        time = 0,
                        dwExtraInfo = UIntPtr.Zero
                    }
                }
            }
        };

        var sent = SendInput((uint)inputs.Length, inputs, Marshal.SizeOf<INPUT>());
        if (sent != inputs.Length)
            throw new InvalidOperationException($"SendInput key failed. sent={sent}");
    }

    private static void SendUnicodeChar(char ch)
    {
        var inputs = new[]
        {
            new INPUT
            {
                type = INPUT_KEYBOARD,
                U = new InputUnion
                {
                    ki = new KEYBDINPUT
                    {
                        wVk = 0,
                        wScan = ch,
                        dwFlags = KEYEVENTF_UNICODE,
                        time = 0,
                        dwExtraInfo = UIntPtr.Zero
                    }
                }
            },
            new INPUT
            {
                type = INPUT_KEYBOARD,
                U = new InputUnion
                {
                    ki = new KEYBDINPUT
                    {
                        wVk = 0,
                        wScan = ch,
                        dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP,
                        time = 0,
                        dwExtraInfo = UIntPtr.Zero
                    }
                }
            }
        };

        var sent = SendInput((uint)inputs.Length, inputs, Marshal.SizeOf<INPUT>());
        if (sent != inputs.Length)
            throw new InvalidOperationException($"SendInput unicode failed. sent={sent}");
    }

    private static void SendMouseButton(uint downFlag, uint upFlag)
    {
        var inputs = new[]
        {
            new INPUT
            {
                type = INPUT_MOUSE,
                U = new InputUnion
                {
                    mi = new MOUSEINPUT
                    {
                        dx = 0,
                        dy = 0,
                        mouseData = 0,
                        dwFlags = downFlag,
                        time = 0,
                        dwExtraInfo = UIntPtr.Zero
                    }
                }
            },
            new INPUT
            {
                type = INPUT_MOUSE,
                U = new InputUnion
                {
                    mi = new MOUSEINPUT
                    {
                        dx = 0,
                        dy = 0,
                        mouseData = 0,
                        dwFlags = upFlag,
                        time = 0,
                        dwExtraInfo = UIntPtr.Zero
                    }
                }
            }
        };

        var sent = SendInput((uint)inputs.Length, inputs, Marshal.SizeOf<INPUT>());
        if (sent != inputs.Length)
            throw new InvalidOperationException($"SendInput mouse failed. sent={sent}");
    }
}
