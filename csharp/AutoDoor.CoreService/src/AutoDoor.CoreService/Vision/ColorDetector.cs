using System;
using System.Drawing;

namespace AutoDoor.CoreService.Vision;

public static class ColorDetector
{
    public static string GetColorAt(int x, int y)
    {
        var color = ScreenshotService.GetPixelColor(x, y);
        return $"#{color.R:X2}{color.G:X2}{color.B:X2}";
    }

    public static bool IsColorMatch(int x, int y, string hexColor, int tolerance = 10)
    {
        try
        {
            hexColor = hexColor.TrimStart('#');
            var r = Convert.ToInt32(hexColor.Substring(0, 2), 16);
            var g = Convert.ToInt32(hexColor.Substring(2, 2), 16);
            var b = Convert.ToInt32(hexColor.Substring(4, 2), 16);

            var actual = ScreenshotService.GetPixelColor(x, y);
            return Math.Abs(actual.R - r) <= tolerance &&
                   Math.Abs(actual.G - g) <= tolerance &&
                   Math.Abs(actual.B - b) <= tolerance;
        }
        catch
        {
            return false;
        }
    }
}
