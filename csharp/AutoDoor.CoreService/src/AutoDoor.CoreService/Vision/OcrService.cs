using System;
using System.Diagnostics;
using System.IO;
using System.Text.Json;
using System.Threading.Tasks;

namespace AutoDoor.CoreService.Vision;

public class OcrResult
{
    public bool Success { get; set; }
    public string Text { get; set; } = "";
    public double Confidence { get; set; }
}

public class OcrService
{
    private readonly string _workerPath;
    private readonly bool _isCommercialBuild;

    public OcrService()
    {
        var baseDir = AppContext.BaseDirectory;
        var possiblePaths = new[]
        {
            Path.Combine(baseDir, "OCRWorker", "OCRWorker.exe"),
            Path.Combine(baseDir, "..", "OCRWorker", "OCRWorker.exe"),
            Path.Combine(baseDir, "tools", "ocr_worker.py"),
            Path.Combine(baseDir, "..", "..", "..", "..", "..", "tools", "ocr_worker.py"),
            Path.Combine(baseDir, "..", "..", "..", "..", "..", "..", "tools", "ocr_worker.py"),
        };

        _workerPath = "";
        _isCommercialBuild = Environment.GetEnvironmentVariable("AUTODOOR_COMMERCIAL_BUILD") == "1"
            || Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT") == "Production";

        foreach (var p in possiblePaths)
        {
            var full = Path.GetFullPath(p);
            if (File.Exists(full))
            {
                _workerPath = full;
                break;
            }
        }
    }

    public bool IsAvailable => !string.IsNullOrEmpty(_workerPath);

    public async Task<OcrResult> RecognizeAsync(string imagePath)
    {
        return await CallWorkerAsync(new { action = "recognize", image_path = imagePath });
    }

    public async Task<OcrResult> RecognizeRegionAsync(int x, int y, int width, int height)
    {
        return await CallWorkerAsync(new { action = "recognize_region", x, y, width, height });
    }

    private async Task<OcrResult> CallWorkerAsync(object input)
    {
        if (string.IsNullOrEmpty(_workerPath))
        {
            return new OcrResult { Success = false, Text = "OCR worker not found in commercial package" };
        }

        try
        {
            var inputJson = JsonSerializer.Serialize(input);

            var isExe = _workerPath.EndsWith(".exe", StringComparison.OrdinalIgnoreCase);
            ProcessStartInfo psi;

            if (isExe)
            {
                psi = new ProcessStartInfo
                {
                    FileName = _workerPath,
                    Arguments = "",
                    RedirectStandardInput = true,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };
            }
            else
            {
                if (_isCommercialBuild)
                {
                    return new OcrResult { Success = false, Text = "OCRWorker.exe not found in commercial package" };
                }

                psi = new ProcessStartInfo
                {
                    FileName = "python",
                    Arguments = $"\"{_workerPath}\"",
                    RedirectStandardInput = true,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };
            }

            using var process = new Process { StartInfo = psi };
            process.Start();

            await process.StandardInput.WriteAsync(inputJson);
            process.StandardInput.Close();

            var output = await process.StandardOutput.ReadToEndAsync();
            await process.WaitForExitAsync();

            if (process.ExitCode != 0)
            {
                var error = await process.StandardError.ReadToEndAsync();
                return new OcrResult { Success = false, Text = $"Worker error: {error}" };
            }

            var result = JsonSerializer.Deserialize<OcrResult>(output);
            return result ?? new OcrResult { Success = false, Text = "Invalid worker response" };
        }
        catch (Exception ex)
        {
            return new OcrResult { Success = false, Text = $"OCR error: {ex.Message}" };
        }
    }
}
