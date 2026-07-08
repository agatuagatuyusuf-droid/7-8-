using System.Threading;
using System.Threading.Tasks;
using AutoDoor.CoreService.BehaviorTree;

namespace AutoDoor.CoreService.Nodes.Actions;

public class SetVariableNode : NodeBase
{
    public override Task<NodeStatus> ExecuteAsync(Blackboard blackboard, CancellationToken ct)
    {
        var variableName = "";
        if (Config.TryGetValue("variable", out var varProp))
            variableName = varProp.GetString() ?? "";

        var value = "true";
        if (Config.TryGetValue("value", out var valProp))
            value = valProp.GetString() ?? value;

        if (!string.IsNullOrEmpty(variableName))
            blackboard.Set(variableName, value);

        return Task.FromResult(NodeStatus.Success);
    }
}
