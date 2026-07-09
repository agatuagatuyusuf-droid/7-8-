using System.Threading;
using System.Threading.Tasks;
using AutoDoor.CoreService.Runtime.NativeInput;

namespace AutoDoor.CoreService.Runtime;

public class CoreActionExecutor
{
    private readonly NativeInputExecutor _nativeInput;

    public CoreActionExecutor(NativeInputExecutor nativeInput)
    {
        _nativeInput = nativeInput;
    }

    public Task<(bool success, string? error, string message)> KeyPressAsync(string key, CancellationToken ct)
    {
        return _nativeInput.KeyPressAsync(key, ct);
    }

    public Task<(bool success, string? error, string message)> TextInputAsync(string text, CancellationToken ct)
    {
        return _nativeInput.TextInputAsync(text, ct);
    }

    public Task<(bool success, string? error, string message)> MouseClickAsync(int x, int y, string button, int count, CancellationToken ct)
    {
        return _nativeInput.MouseClickAsync(x, y, button, count, ct);
    }
}
