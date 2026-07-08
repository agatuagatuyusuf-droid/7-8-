using System;
using System.Threading;
using System.Threading.Tasks;
using AutoDoor.CoreService.BehaviorTree;

namespace AutoDoor.CoreService.Nodes.Actions;

public class KeyPressNode : NodeBase
{
    public override Task<NodeStatus> ExecuteAsync(Blackboard blackboard, CancellationToken ct)
    {
        var key = "";
        if (Config.TryGetValue("key", out var keyProp))
            key = keyProp.GetString() ?? "";

        try
        {
            AutoDoor.CoreService.Input.InputController.KeyPress(key);
            return Task.FromResult(NodeStatus.Success);
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"KeyPressNode error: {ex.Message}");
            return Task.FromResult(NodeStatus.Failure);
        }
    }
}
