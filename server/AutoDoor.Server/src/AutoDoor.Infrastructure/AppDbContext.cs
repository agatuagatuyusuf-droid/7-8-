using Microsoft.EntityFrameworkCore;
using AutoDoor.Server.Domain;

namespace AutoDoor.Server.Infrastructure;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<Admin> Admins => Set<Admin>();
    public DbSet<User> Users => Set<User>();
    public DbSet<Product> Products => Set<Product>();
    public DbSet<Feature> Features => Set<Feature>();
    public DbSet<License> Licenses => Set<License>();
    public DbSet<LicenseFeature> LicenseFeatures => Set<LicenseFeature>();
    public DbSet<Machine> Machines => Set<Machine>();
    public DbSet<ActivationCode> ActivationCodes => Set<ActivationCode>();
    public DbSet<Order> Orders => Set<Order>();
    public DbSet<LicenseSession> LicenseSessions => Set<LicenseSession>();
    public DbSet<VersionRelease> VersionReleases => Set<VersionRelease>();
    public DbSet<AuditLog> AuditLogs => Set<AuditLog>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<ActivationCode>()
            .HasIndex(a => a.Code)
            .IsUnique();

        modelBuilder.Entity<Admin>()
            .HasIndex(a => a.Username)
            .IsUnique();

        modelBuilder.Entity<Product>()
            .HasIndex(a => a.ProductId)
            .IsUnique();
    }
}
