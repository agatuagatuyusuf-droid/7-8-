using System;
using System.Threading;
using System.Threading.Tasks;
using AutoDoor.CoreService.BehaviorTree;

namespace AutoDoor.CoreService.Nodes.Actions;

public class DelayNode : NodeBase
{
    public override async Task<NodeStatus> ExecuteAsync(Blackboard blackboard, CancellationToken ct)
    {
        var delayMs = 1000;
        if (Config.TryGetValue("delay_ms", out var value))
        {
            delayMs = value.GetInt32();
        }

        await Task.Delay(delayMs, ct);
        return NodeStatus.Success;
    }
}
