using System;
using System.Collections.Generic;

namespace AutoDoor.CoreService.BehaviorTree;

public static class NodeRegistry
{
    private static readonly Dictionary<string, Func<NodeBase>> _factories = new();

    static NodeRegistry()
    {
        Register("StartNode", () => new Nodes.Composite.StartNode());
        Register("SequenceNode", () => new Nodes.Composite.SequenceNode());
        Register("SelectorNode", () => new Nodes.Composite.SelectorNode());
        Register("DelayNode", () => new Nodes.Actions.DelayNode());
        Register("LogStatusNode", () => new Nodes.Actions.LogStatusNode());
        Register("SetVariableNode", () => new Nodes.Actions.SetVariableNode());
        Register("VariableConditionNode", () => new Nodes.Conditions.VariableConditionNode());
        Register("KeyPressNode", () => new Nodes.Actions.KeyPressNode());
        Register("MouseClickNode", () => new Nodes.Actions.MouseClickNode());
        Register("TextInputNode", () => new Nodes.Actions.TextInputNode());
        Register("ColorConditionNode", () => new Nodes.Conditions.ColorConditionNode());
        Register("ImageConditionNode", () => new Nodes.Conditions.ImageConditionNode());
        Register("OCRConditionNode", () => new Nodes.Conditions.OcrConditionNode());
    }

    public static void Register(string type, Func<NodeBase> factory)
    {
        _factories[type] = factory;
    }

    public static NodeBase? Create(string type)
    {
        if (_factories.TryGetValue(type, out var factory))
            return factory();
        return null;
    }

    public static bool IsRegistered(string type) => _factories.ContainsKey(type);
}
