using System;
using System.Threading;
using System.Threading.Tasks;
using AutoDoor.CoreService.BehaviorTree;

namespace AutoDoor.CoreService.Nodes.Actions;

public class LogStatusNode : NodeBase
{
    public override Task<NodeStatus> ExecuteAsync(Blackboard blackboard, CancellationToken ct)
    {
        var message = "LogStatusNode executed";
        if (Config.TryGetValue("message", out var value))
        {
            message = value.GetString() ?? message;
        }

        Console.WriteLine($"[BT Runtime] {message}");
        return Task.FromResult(NodeStatus.Success);
    }
}
