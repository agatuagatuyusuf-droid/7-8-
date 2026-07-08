using System;
using System.Linq;
using AutoDoor.Server.Domain;

namespace AutoDoor.Server.Infrastructure;

public static class SeedData
{
    public static void Initialize(AppDbContext db)
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

        var admin = new Admin
        {
            Username = "admin",
            PasswordHash = BCryptPlaceholder("admin123")
        };
        db.Admins.Add(admin);

        var testCode = new ActivationCode
        {
            Code = "TEST-ACTIVATE-123456",
            ProductId = product.Id,
            Edition = "pro",
            DurationDays = 365,
            MachineLimit = 1
        };
        db.ActivationCodes.Add(testCode);

        db.SaveChanges();
    }

    private static string BCryptPlaceholder(string password)
    {
        return $"HASHED:{password}";
    }
}
