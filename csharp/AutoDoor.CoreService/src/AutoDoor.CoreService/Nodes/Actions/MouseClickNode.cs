using System;
using System.Threading;
using System.Threading.Tasks;
using AutoDoor.CoreService.BehaviorTree;

namespace AutoDoor.CoreService.Nodes.Actions;

public class MouseClickNode : NodeBase
{
    public override Task<NodeStatus> ExecuteAsync(Blackboard blackboard, CancellationToken ct)
    {
        NodeBase.GlobalExecutionCount++;
        var button = "left";
        if (Config.TryGetValue("button", out var btnProp))
            button = btnProp?.ToString() ?? "left";

        var x = 0;
        if (Config.TryGetValue("x", out var xProp))
            x = Convert.ToInt32(xProp);

        var y = 0;
        if (Config.TryGetValue("y", out var yProp))
            y = Convert.ToInt32(yProp);

        try
        {
            AutoDoor.CoreService.Input.InputController.MouseClick(button, x, y);
            return Task.FromResult(NodeStatus.Success);
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"MouseClickNode error: {ex.Message}");
            return Task.FromResult(NodeStatus.Failure);
        }
    }
}
