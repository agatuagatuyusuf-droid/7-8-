using System;
using System.Threading;
using System.Threading.Tasks;
using AutoDoor.CoreService.BehaviorTree;

namespace AutoDoor.CoreService.Nodes.Actions;

public class DelayNode : NodeBase
{
    public override async Task<NodeStatus> ExecuteAsync(Blackboard blackboard, CancellationToken ct)
    {
        NodeBase.GlobalExecutionCount++;
        int delayMs = 1000;

        if (Config.TryGetValue("delay_ms", out var delayMsEl))
            delayMs = Convert.ToInt32(delayMsEl);
        else if (Config.TryGetValue("duration_ms", out var durationMsEl))
            delayMs = Convert.ToInt32(durationMsEl);
        else if (Config.TryGetValue("seconds", out var secondsEl))
            delayMs = Convert.ToInt32(secondsEl) * 1000;
        else if (Config.TryGetValue("delay", out var delayEl))
            delayMs = Convert.ToInt32(delayEl);

        if (delayMs > 0)
        {
            try
            {
                await Task.Delay(delayMs, ct);
            }
            catch (OperationCanceledException)
            {
                return NodeStatus.Aborted;
            }
        }

        return NodeStatus.Success;
    }
}
