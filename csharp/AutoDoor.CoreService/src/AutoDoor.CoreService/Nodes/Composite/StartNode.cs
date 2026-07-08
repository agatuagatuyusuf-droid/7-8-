using System.Threading;
using System.Threading.Tasks;
using AutoDoor.CoreService.BehaviorTree;

namespace AutoDoor.CoreService.Nodes.Composite;

public class StartNode : NodeBase
{
    public override async Task<NodeStatus> ExecuteAsync(Blackboard blackboard, CancellationToken ct)
    {
        if (Children.Count == 0)
            return NodeStatus.Success;

        return await Children[0].ExecuteAsync(blackboard, ct);
    }
}
