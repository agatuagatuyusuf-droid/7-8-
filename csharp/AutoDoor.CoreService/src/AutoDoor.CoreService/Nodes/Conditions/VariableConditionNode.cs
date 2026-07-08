using System;
using System.Threading;
using System.Threading.Tasks;
using AutoDoor.CoreService.BehaviorTree;

namespace AutoDoor.CoreService.Nodes.Conditions;

public class VariableConditionNode : NodeBase
{
    public override Task<NodeStatus> ExecuteAsync(Blackboard blackboard, CancellationToken ct)
    {
        var variableName = "";
        if (Config.TryGetValue("variable", out var varProp))
            variableName = varProp.GetString() ?? "";

        var expectedValue = "";
        if (Config.TryGetValue("value", out var valProp))
            expectedValue = valProp.GetString() ?? "";

        var operatorType = "equals";
        if (Config.TryGetValue("operator", out var opProp))
            operatorType = opProp.GetString() ?? "equals";

        var actualValue = blackboard.Get(variableName)?.ToString() ?? "";

        var result = operatorType switch
        {
            "equals" => string.Equals(actualValue, expectedValue, StringComparison.OrdinalIgnoreCase),
            "not_equals" => !string.Equals(actualValue, expectedValue, StringComparison.OrdinalIgnoreCase),
            "contains" => actualValue.Contains(expectedValue, StringComparison.OrdinalIgnoreCase),
            "exists" => blackboard.Has(variableName),
            "not_exists" => !blackboard.Has(variableName),
            _ => string.Equals(actualValue, expectedValue, StringComparison.OrdinalIgnoreCase)
        };

        return Task.FromResult(result ? NodeStatus.Success : NodeStatus.Failure);
    }
}
