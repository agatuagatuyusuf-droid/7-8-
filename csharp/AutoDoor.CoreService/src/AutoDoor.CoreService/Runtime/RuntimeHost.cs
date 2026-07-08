using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using AutoDoor.CoreService.BehaviorTree;

namespace AutoDoor.CoreService.Runtime;

public class RuntimeHost
{
    private readonly object _lock = new();
    private Task? _currentTask;
    private CancellationTokenSource? _cts;
    private BehaviorTreeEngine? _engine;
    private NodeBase? _currentTree;
    private RuntimeContext _context = new();
    private DateTime _startTime;

    public object Status()
    {
        lock (_lock)
        {
            return new
            {
                running = _context.State == RuntimeState.Running,
                paused = _context.State == RuntimeState.Paused,
                completed = _context.State == RuntimeState.Completed || _context.State == RuntimeState.Failed || _context.State == RuntimeState.Aborted,
                status = _context.State.ToString().ToLowerInvariant(),
                tick_count = _context.TickCount,
                elapsed_ms = _context.ElapsedMs,
                last_error = _context.LastError
            };
        }
    }

    public object Logs()
    {
        lock (_lock)
        {
            var logs = _context.Logs.ToArray();
            return new { logs = logs.Select(l => new { l.Timestamp, l.Level, l.Message }).ToArray() };
        }
    }

    public object Stats()
    {
        lock (_lock)
        {
            return new
            {
                trees_started = _context.State != RuntimeState.Idle ? 1 : 0,
                trees_completed = _context.State == RuntimeState.Completed ? 1 : 0,
                total_ticks = _context.TickCount,
                uptime_ms = _context.ElapsedMs
            };
        }
    }

    public (bool success, string? error, string message) StartTree(NodeBase tree)
    {
        lock (_lock)
        {
            if (_context.State == RuntimeState.Running)
                return (false, "ALREADY_RUNNING", "A tree is already running");

            _currentTree = tree;
            _context = new RuntimeContext
            {
                CurrentTreeId = tree.Id,
                State = RuntimeState.Running,
                StartTime = DateTime.UtcNow
            };
            _startTime = DateTime.UtcNow;

            _cts = new CancellationTokenSource();
            _engine = new BehaviorTreeEngine(tree);

            _currentTask = Task.Run(async () =>
            {
                try
                {
                    var status = await _engine.ExecuteAsync(_cts.Token);
                    lock (_lock)
                    {
                        _context.TickCount++;
                        _context.ElapsedMs = (long)(DateTime.UtcNow - _context.StartTime).TotalMilliseconds;
                        _context.State = status switch
                        {
                            NodeStatus.Success => RuntimeState.Completed,
                            NodeStatus.Failure => RuntimeState.Failed,
                            NodeStatus.Aborted => RuntimeState.Aborted,
                            _ => RuntimeState.Completed
                        };
                    }
                }
                catch (Exception ex)
                {
                    lock (_lock)
                    {
                        _context.State = RuntimeState.Failed;
                        _context.LastError = ex.Message;
                    }
                }
            });

            AddLog("Info", "Tree started");
            return (true, null, "Tree started");
        }
    }

    public (bool success, string? error, string message) Stop()
    {
        lock (_lock)
        {
            if (_context.State != RuntimeState.Running && _context.State != RuntimeState.Paused)
                return (false, "NOT_RUNNING", "No tree is running");

            _cts?.Cancel();
            _context.State = RuntimeState.Aborted;
            AddLog("Info", "Tree stopped");
            return (true, null, "Tree stopped");
        }
    }

    public (bool success, string? error, string message) Pause()
    {
        lock (_lock)
        {
            if (_context.State != RuntimeState.Running)
                return (false, "NOT_RUNNING", "No tree is running");

            _context.State = RuntimeState.Paused;
            AddLog("Info", "Tree paused");
            return (true, null, "Tree paused");
        }
    }

    public (bool success, string? error, string message) Resume()
    {
        lock (_lock)
        {
            if (_context.State != RuntimeState.Paused)
                return (false, "NOT_PAUSED", "Tree is not paused");

            _context.State = RuntimeState.Running;
            AddLog("Info", "Tree resumed");
            return (true, null, "Tree resumed");
        }
    }

    public void AddLog(string level, string message)
    {
        lock (_lock)
        {
            _context.Logs.Enqueue(new RuntimeLogEntry
            {
                Timestamp = DateTime.UtcNow,
                Level = level,
                Message = message
            });

            while (_context.Logs.Count > 1000)
                _context.Logs.TryDequeue(out _);
        }
    }
}
