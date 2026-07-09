using System.Threading.Tasks;
using AutoDoor.CoreService.Runtime.NativeInput;
using AutoDoor.CoreService.Security;
using Xunit;

namespace AutoDoor.CoreService.Tests;

public class CoreInputSecurityTests
{
    [Fact]
    public void LoginSessionServiceRejectsEmptyToken()
    {
        var svc = new LoginSessionService();
        Assert.False(svc.Validate(""));
        Assert.False(svc.Validate("bad-token"));
    }

    [Fact]
    public async Task NativeInputExecutorRejectsLongText()
    {
        var executor = new NativeInputExecutor();
        var text = new string('a', 2001);
        var result = await executor.TextInputAsync(text, default);

        Assert.False(result.success);
        Assert.Equal("TEXT_TOO_LONG", result.error);
    }
}
