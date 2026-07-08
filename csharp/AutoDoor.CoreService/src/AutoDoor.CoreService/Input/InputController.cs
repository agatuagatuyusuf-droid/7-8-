using System;
using System.Runtime.InteropServices;

namespace AutoDoor.CoreService.Input;

public static class InputController
{
    [StructLayout(LayoutKind.Sequential)]
    private struct INPUT
    {
        public uint type;
        public InputUnion u;
    }

    [StructLayout(LayoutKind.Explicit)]
    private struct InputUnion
    {
        [FieldOffset(0)] public MOUSEINPUT mi;
        [FieldOffset(0)] public KEYBDINPUT ki;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct MOUSEINPUT
    {
        public int dx;
        public int dy;
        public uint mouseData;
        public uint dwFlags;
        public uint time;
        public IntPtr dwExtraInfo;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct KEYBDINPUT
    {
        public ushort wVk;
        public ushort wScan;
        public uint dwFlags;
        public uint time;
        public IntPtr dwExtraInfo;
    }

    private const uint INPUT_MOUSE = 0;
    private const uint INPUT_KEYBOARD = 1;

    private const uint KEYEVENTF_KEYDOWN = 0x0000;
    private const uint KEYEVENTF_KEYUP = 0x0002;
    private const uint KEYEVENTF_SCANCODE = 0x0008;

    private const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
    private const uint MOUSEEVENTF_LEFTUP = 0x0004;
    private const uint MOUSEEVENTF_RIGHTDOWN = 0x0008;
    private const uint MOUSEEVENTF_RIGHTUP = 0x0010;
    private const uint MOUSEEVENTF_MIDDLEDOWN = 0x0020;
    private const uint MOUSEEVENTF_MIDDLEUP = 0x0040;
    private const uint MOUSEEVENTF_ABSOLUTE = 0x8000;
    private const uint MOUSEEVENTF_MOVE = 0x0001;

    [DllImport("user32.dll", SetLastError = true)]
    private static extern uint SendInput(uint cInputs, INPUT[] pInputs, int cbSize);

    [DllImport("user32.dll")]
    private static extern bool SetCursorPos(int x, int y);

    [DllImport("user32.dll")]
    private static extern short VkKeyScanA(char ch);

    public static void KeyPress(string key)
    {
        if (string.IsNullOrEmpty(key)) return;

        var vk = GetVirtualKeyCode(key);
        if (vk == 0) return;
        SendKey(vk, false);
    }

    public static void MouseClick(string button, int x, int y)
    {
        if (x >= 0 && y >= 0)
            SetCursorPos(x, y);

        uint downFlag = button.ToLowerInvariant() switch
        {
            "right" => MOUSEEVENTF_RIGHTDOWN,
            "middle" => MOUSEEVENTF_MIDDLEDOWN,
            _ => MOUSEEVENTF_LEFTDOWN
        };
        uint upFlag = button.ToLowerInvariant() switch
        {
            "right" => MOUSEEVENTF_RIGHTUP,
            "middle" => MOUSEEVENTF_MIDDLEUP,
            _ => MOUSEEVENTF_LEFTUP
        };

        SendMouse(downFlag);
        SendMouse(upFlag);
    }

    public static void TypeText(string text)
    {
        if (string.IsNullOrEmpty(text)) return;

        foreach (var c in text)
        {
            if (c >= 'a' && c <= 'z')
            {
                var vk = (ushort)(c - 'a' + 0x41);
                SendKey(vk, false);
            }
            else if (c >= 'A' && c <= 'Z')
            {
                var vk = (ushort)(c - 'A' + 0x41);
                SendModifierKey(0x10, vk);
            }
            else if (c >= '0' && c <= '9')
            {
                var vk = (ushort)(c - '0' + 0x30);
                SendKey(vk, false);
            }
            else if (c == ' ')
            {
                SendKey(0x20, false);
            }
            else if (c == '\n')
            {
                SendKey(0x0D, false);
            }
        }
    }

    private static void SendKey(ushort vk, bool isScanCode)
    {
        uint flags = isScanCode ? KEYEVENTF_SCANCODE : KEYEVENTF_KEYDOWN;

        var inputs = new INPUT[2];
        inputs[0] = new INPUT
        {
            type = INPUT_KEYBOARD,
            u = new InputUnion
            {
                ki = new KEYBDINPUT { wVk = vk, dwFlags = flags }
            }
        };
        inputs[1] = new INPUT
        {
            type = INPUT_KEYBOARD,
            u = new InputUnion
            {
                ki = new KEYBDINPUT { wVk = vk, dwFlags = flags | KEYEVENTF_KEYUP }
            }
        };
        SendInput(2, inputs, Marshal.SizeOf<INPUT>());
    }

    private static void SendModifierKey(ushort modifierVk, ushort vk)
    {
        var inputs = new INPUT[4];
        inputs[0] = new INPUT
        {
            type = INPUT_KEYBOARD,
            u = new InputUnion { ki = new KEYBDINPUT { wVk = modifierVk, dwFlags = KEYEVENTF_KEYDOWN } }
        };
        inputs[1] = new INPUT
        {
            type = INPUT_KEYBOARD,
            u = new InputUnion { ki = new KEYBDINPUT { wVk = vk, dwFlags = KEYEVENTF_KEYDOWN } }
        };
        inputs[2] = new INPUT
        {
            type = INPUT_KEYBOARD,
            u = new InputUnion { ki = new KEYBDINPUT { wVk = vk, dwFlags = KEYEVENTF_KEYUP } }
        };
        inputs[3] = new INPUT
        {
            type = INPUT_KEYBOARD,
            u = new InputUnion { ki = new KEYBDINPUT { wVk = modifierVk, dwFlags = KEYEVENTF_KEYUP } }
        };
        SendInput(4, inputs, Marshal.SizeOf<INPUT>());
    }

    private static void SendMouse(uint flags)
    {
        var inputs = new INPUT[1];
        inputs[0] = new INPUT
        {
            type = INPUT_MOUSE,
            u = new InputUnion { mi = new MOUSEINPUT { dwFlags = flags } }
        };
        SendInput(1, inputs, Marshal.SizeOf<INPUT>());
    }

    private static ushort GetVirtualKeyCode(string key)
    {
        if (key.Length == 1 && key[0] >= 'a' && key[0] <= 'z')
            return (ushort)(key[0] - 'a' + 0x41);
        if (key.Length == 1 && key[0] >= 'A' && key[0] <= 'Z')
            return (ushort)(key[0] - 'A' + 0x41);
        if (key.Length == 1 && key[0] >= '0' && key[0] <= '9')
            return (ushort)(key[0] - '0' + 0x30);

        return key.ToLowerInvariant() switch
        {
            "enter" => 0x0D,
            "tab" => 0x09,
            "space" => 0x20,
            "backspace" => 0x08,
            "delete" => 0x2E,
            "escape" => 0x1B,
            "up" => 0x26,
            "down" => 0x28,
            "left" => 0x25,
            "right" => 0x27,
            "ctrl" => 0x11,
            "alt" => 0x12,
            "shift" => 0x10,
            "f1" => 0x70,
            "f2" => 0x71,
            "f3" => 0x72,
            "f4" => 0x73,
            "f5" => 0x74,
            "f6" => 0x75,
            "f7" => 0x76,
            "f8" => 0x77,
            "f9" => 0x78,
            "f10" => 0x79,
            "f11" => 0x7A,
            "f12" => 0x7B,
            _ => 0
        };
    }
}
