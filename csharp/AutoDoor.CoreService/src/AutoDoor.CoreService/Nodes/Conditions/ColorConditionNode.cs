using System;
using System.Threading;
using System.Threading.Tasks;
using AutoDoor.CoreService.BehaviorTree;

namespace AutoDoor.CoreService.Nodes.Conditions;

public class ColorConditionNode : NodeBase
{
    public override Task<NodeStatus> ExecuteAsync(Blackboard blackboard, CancellationToken ct)
    {
        var x = 0; var y = 0;
        if (Config.TryGetValue("x", out var xProp)) x = xProp.GetInt32();
        if (Config.TryGetValue("y", out var yProp)) y = yProp.GetInt32();

        var expectedColor = "";
        if (Config.TryGetValue("color", out var colorProp))
            expectedColor = colorProp.GetString() ?? "";

        try
        {
            var detected = AutoDoor.CoreService.Vision.ColorDetector.GetColorAt(x, y);
            var match = string.Equals(detected, expectedColor, StringComparison.OrdinalIgnoreCase);
            return Task.FromResult(match ? NodeStatus.Success : NodeStatus.Failure);
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"ColorConditionNode error: {ex.Message}");
            return Task.FromResult(NodeStatus.Failure);
        }
    }
}
