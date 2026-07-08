using System;
using System.Collections.Generic;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;

namespace AutoDoor.CoreService.BehaviorTree;

public abstract class NodeBase
{
    public string Id { get; set; } = "";
    public string NodeType { get; set; } = "";
    public string Name { get; set; } = "";
    public Dictionary<string, JsonElement> Config { get; set; } = new();
    public List<NodeBase> Children { get; set; } = new();

    public abstract Task<NodeStatus> ExecuteAsync(Blackboard blackboard, CancellationToken ct);

    public virtual void Reset() { }

    public static NodeBase FromJson(JsonElement element)
    {
        var id = element.TryGetProperty("id", out var idProp) ? idProp.GetString() ?? "" : "";
        id = element.TryGetProperty("node_id", out var nidProp) ? nidProp.GetString() ?? "" : id;

        var type = element.TryGetProperty("type", out var typeProp) ? typeProp.GetString() ?? "" : "";
        type = element.TryGetProperty("node_type", out var ntProp) ? ntProp.GetString() ?? "" : type;

        var name = element.TryGetProperty("name", out var nameProp) ? nameProp.GetString() ?? "" : "";

        var config = new Dictionary<string, JsonElement>();
        if (element.TryGetProperty("config", out var configProp) && configProp.ValueKind == JsonValueKind.Object)
        {
            foreach (var prop in configProp.EnumerateObject())
            {
                config[prop.Name] = prop.Value;
            }
        }

        var children = new List<NodeBase>();
        if (element.TryGetProperty("children", out var childrenProp) && childrenProp.ValueKind == JsonValueKind.Array)
        {
            foreach (var child in childrenProp.EnumerateArray())
            {
                children.Add(FromJson(child));
            }
        }

        var node = NodeRegistry.Create(type);
        if (node == null)
            throw new NotImplementedException($"Node type '{type}' not implemented");

        node.Id = id;
        node.NodeType = type;
        node.Name = name;
        node.Config = config;
        node.Children = children;

        return node;
    }
}
