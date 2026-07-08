using System;
using System.Text;
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using AutoDoor.Server.Infrastructure;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Database: PostgreSQL or InMemory based on configuration
var dbProvider = Environment.GetEnvironmentVariable("AUTODOOR_DB_PROVIDER") 
    ?? builder.Configuration["Database:Provider"] 
    ?? "InMemory";

var connectionString = Environment.GetEnvironmentVariable("AUTODOOR_DB_CONNECTION_STRING")
    ?? builder.Configuration["Database:ConnectionString"]
    ?? "";

builder.Services.AddDbContext<AppDbContext>(options =>
{
    if (dbProvider.Equals("PostgreSQL", StringComparison.OrdinalIgnoreCase) && !string.IsNullOrEmpty(connectionString))
    {
        options.UseNpgsql(connectionString);
    }
    else
    {
        options.UseInMemoryDatabase("AutoDoorServer");
        Console.WriteLine("Using InMemory database (data will be lost on restart)");
    }
});

// JWT Authentication
var jwtSecret = Environment.GetEnvironmentVariable("AUTODOOR_JWT_SECRET")
    ?? builder.Configuration["Jwt:Secret"]
    ?? "CHANGE_ME_DEV_SECRET_MIN_32_CHARS";

var jwtIssuer = Environment.GetEnvironmentVariable("AUTODOOR_JWT_ISSUER")
    ?? builder.Configuration["Jwt:Issuer"]
    ?? "AutoDoor.Server";

var jwtAudience = Environment.GetEnvironmentVariable("AUTODOOR_JWT_AUDIENCE")
    ?? builder.Configuration["Jwt:Audience"]
    ?? "AutoDoor.Admin";

var envName = Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT") ?? "Production";
var isExplicitProduction = string.Equals(envName, "Production", StringComparison.OrdinalIgnoreCase);

if (jwtSecret == "CHANGE_ME_DEV_SECRET_MIN_32_CHARS")
{
    if (isExplicitProduction)
    {
        Console.Error.WriteLine("FATAL: Explicit Production environment requires a secure JWT secret via AUTODOOR_JWT_SECRET");
        Environment.Exit(1);
    }
    Console.WriteLine("WARNING: Using default JWT secret. Set AUTODOOR_JWT_SECRET for production.");
}

builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = jwtIssuer,
            ValidAudience = jwtAudience,
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtSecret))
        };
    });

builder.Services.AddAuthorization();

builder.Services.AddSingleton<TicketSigner>();

builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin().AllowAnyHeader().AllowAnyMethod();
    });
});

var app = builder.Build();

// Seed data
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    SeedData.Initialize(db, app.Environment);
}

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

var port = args.Length > 0 ? args[0] : "5000";
Console.WriteLine($"AutoDoor License Server starting on http://localhost:{port}");
app.Run($"http://0.0.0.0:{port}");