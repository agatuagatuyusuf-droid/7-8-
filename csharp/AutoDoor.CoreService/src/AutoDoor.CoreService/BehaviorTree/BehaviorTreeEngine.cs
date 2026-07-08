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

    public async Task<NodeStatus> ExecuteAsync(CancellationToken ct)
    {
        try
        {
            return await _root.ExecuteAsync(_blackboard, ct);
        }
        catch (OperationCanceledException)
        {
            return NodeStatus.Aborted;
        }
        catch (Exception)
        {
            return NodeStatus.Failure;
        }
    }
}
