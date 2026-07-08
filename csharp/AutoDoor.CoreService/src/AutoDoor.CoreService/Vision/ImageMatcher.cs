using System;
using System.IO;

namespace AutoDoor.CoreService.Vision;

public class ImageMatchResult
{
    public bool Found { get; set; }
    public double Score { get; set; }
    public int X { get; set; }
    public int Y { get; set; }
    public int Width { get; set; }
    public int Height { get; set; }
}

public class ImageMatcher
{
    private readonly bool _available;

    public ImageMatcher()
    {
        try
        {
            OpenCvSharp.Cv2.GetTickCount();
            _available = true;
        }
        catch
        {
            _available = false;
        }
    }

    public bool IsAvailable => _available;

    public ImageMatchResult MatchTemplate(string templatePath, double threshold = 0.8)
    {
        if (!_available)
            return FallbackResult("OpenCvSharp4 not available");

        if (!File.Exists(templatePath))
            return new ImageMatchResult { Found = false, Score = 0 };

        try
        {
            using var screenshot = CaptureScreen();
            using var templ = new OpenCvSharp.Mat(templatePath, OpenCvSharp.ImreadModes.Color);

            if (templ.Empty() || screenshot.Empty())
                return new ImageMatchResult { Found = false, Score = 0 };

            using var result = new OpenCvSharp.Mat();
            OpenCvSharp.Cv2.MatchTemplate(screenshot, templ, result, OpenCvSharp.TemplateMatchModes.CCoeffNormed);
            OpenCvSharp.Cv2.MinMaxLoc(result, out _, out double maxVal, out _, out OpenCvSharp.Point maxLoc);

            if (maxVal >= threshold)
            {
                return new ImageMatchResult
                {
                    Found = true,
                    Score = maxVal,
                    X = maxLoc.X,
                    Y = maxLoc.Y,
                    Width = templ.Width,
                    Height = templ.Height
                };
            }

            return new ImageMatchResult { Found = false, Score = maxVal };
        }
        catch (Exception)
        {
            return new ImageMatchResult { Found = false, Score = 0 };
        }
    }

    public ImageMatchResult MatchTemplateInRegion(string templatePath, int x, int y, int width, int height, double threshold = 0.8)
    {
        if (!_available)
            return FallbackResult("OpenCvSharp4 not available");

        if (!File.Exists(templatePath))
            return new ImageMatchResult { Found = false, Score = 0 };

        try
        {
            using var screenshot = CaptureScreen();
            using var templ = new OpenCvSharp.Mat(templatePath, OpenCvSharp.ImreadModes.Color);

            if (templ.Empty() || screenshot.Empty())
                return new ImageMatchResult { Found = false, Score = 0 };

            var regionX = Math.Max(0, x);
            var regionY = Math.Max(0, y);
            var regionW = Math.Min(width, screenshot.Width - regionX);
            var regionH = Math.Min(height, screenshot.Height - regionY);

            if (regionW <= 0 || regionH <= 0)
                return new ImageMatchResult { Found = false, Score = 0 };

            using var region = new OpenCvSharp.Mat(screenshot, new OpenCvSharp.Rect(regionX, regionY, regionW, regionH));
            using var result = new OpenCvSharp.Mat();
            OpenCvSharp.Cv2.MatchTemplate(region, templ, result, OpenCvSharp.TemplateMatchModes.CCoeffNormed);
            OpenCvSharp.Cv2.MinMaxLoc(result, out _, out double maxVal, out _, out OpenCvSharp.Point maxLoc);

            if (maxVal >= threshold)
            {
                return new ImageMatchResult
                {
                    Found = true,
                    Score = maxVal,
                    X = regionX + maxLoc.X,
                    Y = regionY + maxLoc.Y,
                    Width = templ.Width,
                    Height = templ.Height
                };
            }

            return new ImageMatchResult { Found = false, Score = maxVal };
        }
        catch (Exception)
        {
            return new ImageMatchResult { Found = false, Score = 0 };
        }
    }

    private static OpenCvSharp.Mat CaptureScreen()
    {
        var primaryScreen = System.Windows.Forms.Screen.PrimaryScreen;
        var bounds = primaryScreen != null ? primaryScreen.Bounds : new System.Drawing.Rectangle(0, 0, 1920, 1080);
        var width = bounds.Width;
        var height = bounds.Height;

        using var bitmap = new System.Drawing.Bitmap(width, height, System.Drawing.Imaging.PixelFormat.Format32bppArgb);
        using var g = System.Drawing.Graphics.FromImage(bitmap);
        g.CopyFromScreen(0, 0, 0, 0, bitmap.Size);

        return OpenCvSharp.Extensions.BitmapConverter.ToMat(bitmap);
    }

    private static ImageMatchResult FallbackResult(string reason)
    {
        return new ImageMatchResult { Found = false, Score = 0 };
    }
}
