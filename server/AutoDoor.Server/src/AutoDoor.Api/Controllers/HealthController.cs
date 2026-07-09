using System;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using AutoDoor.Server.Infrastructure;

namespace AutoDoor.Server.Api.Controllers;

[ApiController]
public class HealthController : ControllerBase
{
    [HttpGet("/health")]
    public IActionResult Health()
    {
        return Ok(new
        {
            success = true,
            status = "healthy",
            time = DateTime.UtcNow
        });
    }

    [HttpGet("/ready")]
    public async Task<IActionResult> Ready(
        [FromServices] AppDbContext db,
        [FromServices] TicketSigner signer)
    {
        bool databaseReady;
        try
        {
            databaseReady = await db.Database.CanConnectAsync();
        }
        catch
        {
            databaseReady = false;
        }

        return Ok(new
        {
            success = databaseReady && signer.HasPrivateKey,
            database = databaseReady,
            signing_key = signer.HasPrivateKey,
            time = DateTime.UtcNow
        });
    }
}
