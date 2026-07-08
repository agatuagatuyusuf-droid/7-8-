using System;
using System.Collections.Concurrent;
using System.Collections.Generic;

namespace AutoDoor.CoreService.Runtime;

public class RuntimeContext
{
    public string CurrentTreeId { get; set; } = "";
    public RuntimeState State { get; set; } = RuntimeState.Idle;
    public int TickCount { get; set; }
    public DateTime StartTime { get; set; }
    public long ElapsedMs { get; set; }
    public string? LastError { get; set; }
    public ConcurrentQueue<RuntimeLogEntry> Logs { get; } = new();
}

public class RuntimeLogEntry
{
    public DateTime Timestamp { get; set; }
    public string Level { get; set; } = "Info";
    public string Message { get; set; } = "";
}
