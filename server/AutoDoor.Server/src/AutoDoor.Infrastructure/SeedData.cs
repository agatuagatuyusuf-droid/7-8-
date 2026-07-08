using System;
using System.Linq;
using Microsoft.Extensions.Hosting;
using AutoDoor.Server.Domain;

namespace AutoDoor.Server.Infrastructure;

public static class SeedData
{
    public static void Initialize(AppDbContext db, IHostEnvironment environment)
    {
        if (db.Products.Any()) return;

        var product = new Product
        {
            ProductId = "autodoor_pro",
            Name = "AutoDoor Pro",
            Description = "AutoDoor Professional Edition"
        };
        db.Products.Add(product);

        var features = new[]
        {
            new Feature { FeatureCode = "basic_editor", Name = "Basic Editor" },
            new Feature { FeatureCode = "basic_input", Name = "Basic Input" },
            new Feature { FeatureCode = "schedule", Name = "Schedule" },
            new Feature { FeatureCode = "ocr", Name = "OCR" },
            new Feature { FeatureCode = "image_match", Name = "Image Match" },
        };
        db.Features.AddRange(features);

        // Admin user - production reads from env vars, development uses default
        if (environment.IsDevelopment())
        {
            var admin = new Admin
            {
                Username = "admin",
                PasswordHash = BCrypt.Net.BCrypt.HashPassword("admin123")
            };
            db.Admins.Add(admin);
        }
        else
        {
            var adminUsername = Environment.GetEnvironmentVariable("AUTODOOR_ADMIN_USERNAME");
            var adminPassword = Environment.GetEnvironmentVariable("AUTODOOR_ADMIN_PASSWORD");

            if (string.IsNullOrEmpty(adminUsername) || string.IsNullOrEmpty(adminPassword))
            {
                Console.Error.WriteLine("WARNING: Production environment without AUTODOOR_ADMIN_USERNAME/AUTODOOR_ADMIN_PASSWORD. No admin user created.");
                Console.Error.WriteLine("Create an admin manually or set these environment variables.");
            }
            else
            {
                var admin = new Admin
                {
                    Username = adminUsername,
                    PasswordHash = BCrypt.Net.BCrypt.HashPassword(adminPassword)
                };
                db.Admins.Add(admin);
            }
        }

        // Test activation code - Development only
        if (environment.IsDevelopment())
        {
            var testCode = new ActivationCode
            {
                Code = "TEST-ACTIVATE-123456",
                ProductId = product.Id,
                Edition = "pro",
                DurationDays = 365,
                MachineLimit = 1
            };
            db.ActivationCodes.Add(testCode);
        }

        db.SaveChanges();
    }
}