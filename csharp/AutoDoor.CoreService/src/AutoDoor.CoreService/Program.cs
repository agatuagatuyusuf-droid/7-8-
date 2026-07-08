using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using AutoDoor.CoreService.Common;
using AutoDoor.CoreService.Ipc;
using AutoDoor.CoreService.License;
using AutoDoor.CoreService.Runtime;

namespace AutoDoor.CoreService;

public class Program
{
    public static async Task<int> Main(string[] args)
    {
        Console.WriteLine("AutoDoor.CoreService starting...");

        var appSettings = AppSettings.Load();

        Console.WriteLine($"TCP IPC listening on {appSettings.Ipc.Host}:{appSettings.Ipc.Port}");

        var services = new ServiceCollection();
        ConfigureServices(services, appSettings);

        var serviceProvider = services.BuildServiceProvider();

        var ipcServer = serviceProvider.GetRequiredService<TcpIpcServer>();
        var cts = new CancellationTokenSource();

        Console.CancelKeyPress += (_, e) =>
        {
            e.Cancel = true;
            cts.Cancel();
        };

        try
        {
            await ipcServer.StartAsync(cts.Token);
            await Task.Delay(Timeout.Infinite, cts.Token);
        }
        catch (OperationCanceledException)
        {
            Console.WriteLine("CoreService shutting down...");
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"Fatal error: {ex.Message}");
            return 1;
        }
        finally
        {
            ipcServer.Stop();
        }

        return 0;
    }

    private static void ConfigureServices(IServiceCollection services, AppSettings appSettings)
    {
        services.AddSingleton(appSettings);
        services.AddSingleton(appSettings.License);
        services.AddSingleton(appSettings.Ipc);
        services.AddSingleton(appSettings.Logging);
        services.AddSingleton<RuntimeHost>();
        services.AddSingleton<TcpIpcServer>();
        services.AddSingleton<LicenseClient>();
        services.AddSingleton<LicenseGuard>();
        services.AddSingleton<MachineCodeProvider>();
        services.AddSingleton<LicenseCache>();
        services.AddSingleton<SignatureVerifier>();
        services.AddSingleton<FeatureGate>();
    }
}
