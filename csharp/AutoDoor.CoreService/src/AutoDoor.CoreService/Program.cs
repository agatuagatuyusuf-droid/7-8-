using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using AutoDoor.CoreService.Ipc;
using AutoDoor.CoreService.License;

namespace AutoDoor.CoreService;

public class Program
{
    public static async Task<int> Main(string[] args)
    {
        Console.WriteLine("AutoDoor.CoreService starting...");

        var services = new ServiceCollection();
        ConfigureServices(services);

        var serviceProvider = services.BuildServiceProvider();

        var ipcServer = serviceProvider.GetRequiredService<IpcServer>();
        var cts = new CancellationTokenSource();

        Console.CancelKeyPress += (_, e) =>
        {
            e.Cancel = true;
            cts.Cancel();
        };

        try
        {
            await ipcServer.StartAsync(cts.Token);
            Console.WriteLine("CoreService running. Press Ctrl+C to exit.");
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

    private static void ConfigureServices(IServiceCollection services)
    {
        services.AddSingleton<IpcServer>();
        services.AddSingleton<LicenseClient>();
        services.AddSingleton<LicenseGuard>();
        services.AddSingleton<MachineCodeProvider>();
        services.AddSingleton<LicenseCache>();
        services.AddSingleton<SignatureVerifier>();
        services.AddSingleton<FeatureGate>();
    }
}
