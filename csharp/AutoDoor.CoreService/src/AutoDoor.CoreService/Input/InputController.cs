using System;
using System.Runtime.InteropServices;

namespace AutoDoor.CoreService.Input;

public static class InputController
{
    public static void KeyPress(string key)
    {
        if (string.IsNullOrEmpty(key)) return;

        var vk = GetVirtualKeyCode(key);
        if (vk == 0) return;

        keybd_event(vk, 0, 0, 0);
        keybd_event(vk, 0, 2, 0);
    }

    public static void MouseClick(string button, int x, int y)
    {
        SetCursorPos(x, y);

        uint downFlag = button.ToLowerInvariant() switch
        {
            "right" => 0x0008,
            "middle" => 0x0020,
            _ => 0x0002
        };
        uint upFlag = button.ToLowerInvariant() switch
        {
            "right" => 0x0010,
            "middle" => 0x0040,
            _ => 0x0004
        };

        mouse_event(downFlag, 0, 0, 0, 0);
        mouse_event(upFlag, 0, 0, 0, 0);
    }

    public static void TypeText(string text)
    {
        if (string.IsNullOrEmpty(text)) return;

        foreach (var c in text)
        {
            if (c >= 'a' && c <= 'z')
            {
                var vk = (byte)(c - 'a' + 0x41);
                keybd_event(vk, 0, 0, 0);
                keybd_event(vk, 0, 2, 0);
            }
            else if (c >= 'A' && c <= 'Z')
            {
                var vk = (byte)(c - 'A' + 0x41);
                keybd_event(0x10, 0, 0, 0);
                keybd_event(vk, 0, 0, 0);
                keybd_event(vk, 0, 2, 0);
                keybd_event(0x10, 0, 2, 0);
            }
            else if (c >= '0' && c <= '9')
            {
                var vk = (byte)(c - '0' + 0x30);
                keybd_event(vk, 0, 0, 0);
                keybd_event(vk, 0, 2, 0);
            }
            else if (c == ' ')
            {
                keybd_event(0x20, 0, 0, 0);
                keybd_event(0x20, 0, 2, 0);
            }
            else if (c == '\n')
            {
                keybd_event(0x0D, 0, 0, 0);
                keybd_event(0x0D, 0, 2, 0);
            }
        }
    }

    private static byte GetVirtualKeyCode(string key)
    {
        if (key.Length == 1 && key[0] >= 'a' && key[0] <= 'z')
            return (byte)(key[0] - 'a' + 0x41);
        if (key.Length == 1 && key[0] >= 'A' && key[0] <= 'Z')
            return (byte)(key[0] - 'A' + 0x41);
        if (key.Length == 1 && key[0] >= '0' && key[0] <= '9')
            return (byte)(key[0] - '0' + 0x30);

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

    [DllImport("user32.dll")]
    private static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, uint dwExtraInfo);

    [DllImport("user32.dll")]
    private static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, uint dwExtraInfo);

    [DllImport("user32.dll")]
    private static extern bool SetCursorPos(int x, int y);
}
