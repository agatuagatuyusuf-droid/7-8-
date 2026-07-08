using System.Threading;
using System.Threading.Tasks;
using AutoDoor.CoreService.BehaviorTree;

namespace AutoDoor.CoreService.Nodes.Composite;

public class SelectorNode : NodeBase
{
    public override async Task<NodeStatus> ExecuteAsync(Blackboard blackboard, CancellationToken ct)
    {
        NodeBase.GlobalExecutionCount++;
        foreach (var child in Children)
        {
            var status = await child.ExecuteAsync(blackboard, ct);
            if (status == NodeStatus.Success)
                return NodeStatus.Success;
        }
        return NodeStatus.Failure;
    }
}
