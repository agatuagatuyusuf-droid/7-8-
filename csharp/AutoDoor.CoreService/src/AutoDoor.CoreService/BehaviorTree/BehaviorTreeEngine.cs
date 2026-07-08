using System;
using System.Threading;
using System.Threading.Tasks;

namespace AutoDoor.CoreService.BehaviorTree;

public class BehaviorTreeEngine
{
    private readonly NodeBase _root;
    private readonly Blackboard _blackboard;

    public BehaviorTreeEngine(NodeBase root, Blackboard? blackboard = null)
    {
        _root = root;
        _blackboard = blackboard ?? new Blackboard();
    }

    public Blackboard Blackboard => _blackboard;
    public int NodesExecuted { get; private set; }

    public async Task<NodeStatus> ExecuteAsync(CancellationToken ct)
    {
        NodeBase.GlobalExecutionCount = 0;
        try
        {
            var result = await _root.ExecuteAsync(_blackboard, ct);
            NodesExecuted = NodeBase.GlobalExecutionCount;
            return result;
        }
        catch (OperationCanceledException)
        {
            return NodeStatus.Aborted;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"BT engine error: {ex.GetType().Name}: {ex.Message}");
            return NodeStatus.Failure;
        }
    }
}
