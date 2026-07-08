using System;
using System.Threading;
using System.Threading.Tasks;
using AutoDoor.CoreService.BehaviorTree;
using AutoDoor.CoreService.Vision;

namespace AutoDoor.CoreService.Nodes.Conditions;

public class OcrConditionNode : NodeBase
{
    public override async Task<NodeStatus> ExecuteAsync(Blackboard blackboard, CancellationToken ct)
    {
        NodeBase.GlobalExecutionCount++;
        var text = "";
        if (Config.TryGetValue("text", out var textProp))
            text = textProp?.ToString() ?? "";

        var imagePath = "";
        if (Config.TryGetValue("image", out var imgProp))
            imagePath = imgProp?.ToString() ?? "";

        try
        {
            var ocr = new OcrService();
            if (!ocr.IsAvailable)
            {
                GlobalLogCallback?.Invoke("Warning", "OCR service not available - ocr_worker.py not found");
                return NodeStatus.Failure;
            }

            OcrResult result;
            if (!string.IsNullOrEmpty(imagePath))
            {
                result = await ocr.RecognizeAsync(imagePath);
            }
            else
            {
                var x = 0; var y = 0; var w = 0; var h = 0;
                if (Config.TryGetValue("x", out var xProp)) x = Convert.ToInt32(xProp);
                if (Config.TryGetValue("y", out var yProp)) y = Convert.ToInt32(yProp);
                if (Config.TryGetValue("width", out var wProp)) w = Convert.ToInt32(wProp);
                if (Config.TryGetValue("height", out var hProp)) h = Convert.ToInt32(hProp);
                result = await ocr.RecognizeRegionAsync(x, y, w, h);
            }

            if (!result.Success)
            {
                GlobalLogCallback?.Invoke("Warning", $"OCR failed: {result.Text}");
                return NodeStatus.Failure;
            }

            if (string.IsNullOrEmpty(text))
                return result.Success ? NodeStatus.Success : NodeStatus.Failure;

            var contains = result.Text.Contains(text, StringComparison.OrdinalIgnoreCase);
            GlobalLogCallback?.Invoke("Info", $"OCR text='{result.Text}' contains='{text}' -> {contains}");
            return contains ? NodeStatus.Success : NodeStatus.Failure;
        }
        catch (Exception ex)
        {
            GlobalLogCallback?.Invoke("Error", $"OcrConditionNode error: {ex.Message}");
            return NodeStatus.Failure;
        }
    }
}
