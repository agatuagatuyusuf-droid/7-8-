using System;
using System.Threading;
using System.Threading.Tasks;
using AutoDoor.CoreService.BehaviorTree;

namespace AutoDoor.CoreService.Nodes.Conditions;

public class ImageConditionNode : NodeBase
{
    public override Task<NodeStatus> ExecuteAsync(Blackboard blackboard, CancellationToken ct)
    {
        NodeBase.GlobalExecutionCount++;
        throw new NotImplementedException("ImageConditionNode is not yet implemented in the commercial build");
    }
}
