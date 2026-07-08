using System;
using System.Drawing;
using System.Runtime.InteropServices;

namespace AutoDoor.CoreService.Vision;

public static class ScreenshotService
{
    public static Color GetPixelColor(int x, int y)
    {
        IntPtr hdc = GetDC(IntPtr.Zero);
        int pixel = GetPixel(hdc, x, y);
        ReleaseDC(IntPtr.Zero, hdc);

        return Color.FromArgb(
            (pixel >> 0) & 0xFF,
            (pixel >> 8) & 0xFF,
            (pixel >> 16) & 0xFF
        );
    }

    [DllImport("user32.dll")]
    private static extern IntPtr GetDC(IntPtr hWnd);

    [DllImport("user32.dll")]
    private static extern int ReleaseDC(IntPtr hWnd, IntPtr hDC);

    [DllImport("gdi32.dll")]
    private static extern int GetPixel(IntPtr hdc, int x, int y);
}
