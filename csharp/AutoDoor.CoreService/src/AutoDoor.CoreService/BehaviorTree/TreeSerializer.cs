using System;
using System.Text.Json;

namespace AutoDoor.CoreService.BehaviorTree;

public static class TreeSerializer
{
    public static NodeBase Deserialize(string json)
    {
        using var doc = JsonDocument.Parse(json);
        return NodeBase.FromJson(doc.RootElement);
    }

    public static NodeBase Deserialize(JsonElement element)
    {
        return NodeBase.FromJson(element);
    }
}
