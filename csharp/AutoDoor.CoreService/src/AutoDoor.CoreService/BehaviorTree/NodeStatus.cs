using System.Text.Json.Serialization;

namespace AutoDoor.CoreService.BehaviorTree;

[JsonConverter(typeof(JsonStringEnumConverter))]
public enum NodeStatus
{
    Success,
    Failure,
    Running,
    Aborted
}
