using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using AutoDoor.CoreService.BehaviorTree;
using AutoDoor.CoreService.Vision;

namespace AutoDoor.CoreService.Nodes.Conditions;

public class ImageConditionNode : NodeBase
{
    public override async Task<NodeStatus> ExecuteAsync(Blackboard blackboard, CancellationToken ct)
    {
        NodeBase.GlobalExecutionCount++;

        try
        {
            var templatePath = "";
            if (Config.TryGetValue("template_path", out var tp))
                templatePath = tp?.ToString() ?? "";
            if (string.IsNullOrEmpty(templatePath) && Config.TryGetValue("image", out var img))
                templatePath = img?.ToString() ?? "";

            if (string.IsNullOrEmpty(templatePath))
            {
                GlobalLogCallback?.Invoke("Warning", "ImageConditionNode: no template_path or image configured");
                return NodeStatus.Failure;
            }

            if (!File.Exists(templatePath))
            {
                GlobalLogCallback?.Invoke("Warning", $"ImageConditionNode: template not found: {templatePath}");
                return NodeStatus.Failure;
            }

            var threshold = 0.8;
            if (Config.TryGetValue("threshold", out var thProp))
                threshold = Convert.ToDouble(thProp);

            var matcher = new ImageMatcher();
            if (!matcher.IsAvailable)
            {
                GlobalLogCallback?.Invoke("Warning", "ImageConditionNode: OpenCvSharp runtime not available");
                return NodeStatus.Failure;
            }

            ImageMatchResult result;
            var useRegion = false;
            if (Config.TryGetValue("use_region", out var urProp))
                useRegion = Convert.ToBoolean(urProp);

            var width = 0;
            var height = 0;
            if (Config.TryGetValue("width", out var wProp)) width = Convert.ToInt32(wProp);
            if (Config.TryGetValue("height", out var hProp)) height = Convert.ToInt32(hProp);

            if (useRegion || (width > 0 && height > 0))
            {
                var x = 0;
                var y = 0;
                if (Config.TryGetValue("x", out var xProp)) x = Convert.ToInt32(xProp);
                if (Config.TryGetValue("y", out var yProp)) y = Convert.ToInt32(yProp);
                result = matcher.MatchTemplateInRegion(templatePath, x, y, width, height, threshold);
            }
            else
            {
                result = matcher.MatchTemplate(templatePath, threshold);
            }

            blackboard.Set("last_image_match", result);
            blackboard.Set("last_detection_position", new { x = result.X, y = result.Y });

            GlobalLogCallback?.Invoke("Info", $"Image match score={result.Score}, found={result.Found}");

            return result.Found ? NodeStatus.Success : NodeStatus.Failure;
        }
        catch (Exception ex)
        {
            GlobalLogCallback?.Invoke("Error", $"ImageConditionNode error: {ex.Message}");
            return NodeStatus.Failure;
        }
    }
}
