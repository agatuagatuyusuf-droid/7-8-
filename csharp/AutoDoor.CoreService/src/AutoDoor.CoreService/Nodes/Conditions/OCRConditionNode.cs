using System;
using System.Threading;
using System.Threading.Tasks;
using AutoDoor.CoreService.BehaviorTree;

namespace AutoDoor.CoreService.Nodes.Conditions;

public class OcrConditionNode : NodeBase
{
    public override Task<NodeStatus> ExecuteAsync(Blackboard blackboard, CancellationToken ct)
    {
        throw new NotImplementedException("OcrConditionNode is not yet implemented in the commercial build");
    }
}
