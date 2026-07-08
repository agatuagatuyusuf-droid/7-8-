using System;
using System.Threading;
using System.Threading.Tasks;
using AutoDoor.CoreService.BehaviorTree;

namespace AutoDoor.CoreService.Nodes.Actions;

public class TextInputNode : NodeBase
{
    public override Task<NodeStatus> ExecuteAsync(Blackboard blackboard, CancellationToken ct)
    {
        NodeBase.GlobalExecutionCount++;
        var text = "";
        if (Config.TryGetValue("text", out var textProp))
            text = textProp?.ToString() ?? "";

        try
        {
            AutoDoor.CoreService.Input.InputController.TypeText(text);
            return Task.FromResult(NodeStatus.Success);
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"TextInputNode error: {ex.Message}");
            return Task.FromResult(NodeStatus.Failure);
        }
    }
}
