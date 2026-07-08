using System.Collections.Concurrent;

namespace AutoDoor.CoreService.BehaviorTree;

public class Blackboard
{
    private readonly ConcurrentDictionary<string, object?> _data = new();

    public void Set(string key, object? value) => _data[key] = value;

    public T? Get<T>(string key) where T : class
    {
        if (_data.TryGetValue(key, out var value) && value is T tValue)
            return tValue;
        return null;
    }

    public object? Get(string key)
    {
        _data.TryGetValue(key, out var value);
        return value;
    }

    public bool Has(string key) => _data.ContainsKey(key);

    public void Clear() => _data.Clear();

    public ConcurrentDictionary<string, object?> GetAll() => _data;
}
