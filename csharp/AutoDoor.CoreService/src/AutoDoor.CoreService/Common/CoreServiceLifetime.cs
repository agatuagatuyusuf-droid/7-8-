using System;
using System.Threading;

namespace AutoDoor.CoreService.Common;

public class CoreServiceLifetime
{
    private readonly CancellationTokenSource _cts = new();

    public CancellationToken Token => _cts.Token;

    public void RequestShutdown()
    {
        if (!_cts.IsCancellationRequested)
            _cts.Cancel();
    }
}
