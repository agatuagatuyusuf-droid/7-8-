using System;
using System.Threading;
using System.Threading.Tasks;
using AutoDoor.CoreService.BehaviorTree;

namespace AutoDoor.CoreService.Nodes.Actions;

public class LogStatusNode : NodeBase
{
    public override Task<NodeStatus> ExecuteAsync(Blackboard blackboard, CancellationToken ct)
    {
        NodeBase.GlobalExecutionCount++;
        var message = "LogStatusNode executed";
        if (Config.TryGetValue("message", out var value))
        {
            message = value?.ToString() ?? message;
        }

        var level = "Info";
        if (Config.TryGetValue("level", out var levelProp))
        {
            level = levelProp?.ToString() ?? level;
        }

        GlobalLogCallback?.Invoke(level, message);
        Console.WriteLine($"[BT Runtime] {message}");
        return Task.FromResult(NodeStatus.Success);
    }
}
