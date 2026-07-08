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

        var lifetime = serviceProvider.GetRequiredService<CoreServiceLifetime>();
        var ipcServer = serviceProvider.GetRequiredService<TcpIpcServer>();

        Console.CancelKeyPress += (_, e) =>
        {
            e.Cancel = true;
            lifetime.RequestShutdown();
        };

        try
        {
            await ipcServer.StartAsync(lifetime.Token);
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

        Console.WriteLine("CoreService exited.");
        return 0;
    }

    private static void ConfigureServices(IServiceCollection services, AppSettings appSettings)
    {
        services.AddSingleton(appSettings);
        services.AddSingleton(appSettings.License);
        services.AddSingleton(appSettings.Ipc);
        services.AddSingleton(appSettings.Logging);
        services.AddSingleton<CoreServiceLifetime>();
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
