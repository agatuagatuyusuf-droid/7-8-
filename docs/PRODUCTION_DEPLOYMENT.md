# AutoDoor Pro Production Deployment Guide

## Architecture

```
Client (AutoDoor Pro) <--HTTPS--> Nginx <--HTTP--> ASP.NET Core API <--> PostgreSQL
                                    |
                                    +--> Static files (optional)
```

## Server Requirements

- .NET 8 Runtime
- PostgreSQL 16+
- (Optional) Redis for session caching
- (Optional) Nginx for reverse proxy

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `AUTODOOR_DB_CONNECTION_STRING` | Yes | PostgreSQL connection string |
| `AUTODOOR_DB_PROVIDER` | No | Set to "PostgreSQL" for production |
| `AUTODOOR_SERVER_PRIVATE_KEY_PATH` | Yes* | Path to RSA private key PEM file |
| `AUTODOOR_SERVER_PRIVATE_KEY_PEM` | Yes* | RSA private key PEM content (alternative to path) |
| `AUTODOOR_JWT_SECRET` | Yes | Min 32 chars, random string for JWT signing |
| `AUTODOOR_JWT_ISSUER` | No | JWT issuer (default: AutoDoor.Server) |
| `AUTODOOR_JWT_AUDIENCE` | No | JWT audience (default: AutoDoor.Admin) |
| `AUTODOOR_ADMIN_USERNAME` | Yes | Initial admin username |
| `AUTODOOR_ADMIN_PASSWORD` | Yes | Initial admin password |
| `ASPNETCORE_ENVIRONMENT` | Yes | Set to "Production" |

*One of AUTODOOR_SERVER_PRIVATE_KEY_PATH or AUTODOOR_SERVER_PRIVATE_KEY_PEM is required.

## First Deployment

### 1. Database Setup

```bash
# Using docker-compose
cd server/AutoDoor.Server
docker-compose up -d postgres

# Or manual PostgreSQL setup
CREATE DATABASE autodoor;
CREATE USER autodoor WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE autodoor TO autodoor;
```

### 2. Generate RSA Key Pair

```bash
# Generate private key
openssl genrsa -out private_key.pem 2048

# Extract public key
openssl rsa -in private_key.pem -pubout -out public_key.pem

# Secure the private key
chmod 600 private_key.pem
```

### 3. Configure Environment

```bash
export ASPNETCORE_ENVIRONMENT=Production
export AUTODOOR_DB_CONNECTION_STRING="Host=localhost;Port=5432;Database=autodoor;Username=autodoor;Password=your_secure_password"
export AUTODOOR_DB_PROVIDER=PostgreSQL
export AUTODOOR_SERVER_PRIVATE_KEY_PATH=/etc/autodoor/keys/private_key.pem
export AUTODOOR_JWT_SECRET="your-32-plus-char-random-string-here"
export AUTODOOR_ADMIN_USERNAME=admin
export AUTODOOR_ADMIN_PASSWORD="your-secure-admin-password"
```

### 4. Run Server

```bash
cd server/AutoDoor.Server
dotnet run --project src/AutoDoor.Api --configuration Release
```

Or using Docker:

```bash
cd server/AutoDoor.Server
docker-compose up -d server
```

### 5. Create Product and Activation Codes

After first login, use the admin API to create products and activation codes:

```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:5000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}' | python -c "import sys,json; print(json.load(sys.stdin)['token'])")

# Create activation code
curl -X POST http://localhost:5000/api/admin/activation-codes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"code":"PROD-2024-XXXX-XXXX","edition":"pro","durationDays":365,"machineLimit":1}'
```

## Client Configuration

The client (AutoDoor Pro) needs:

1. Set server URL: `AUTODOOR_LICENSE_SERVER_URL` env var or in app settings
2. Set public key: `AUTODOOR_LICENSE_PUBLIC_KEY` or `AUTODOOR_LICENSE_PUBLIC_KEY_PATH` env var

## Backup

```bash
# Backup PostgreSQL
pg_dump -U autodoor autodoor > autodoor_backup_$(date +%Y%m%d).sql
```

## Version Update Process

1. Build new CoreService version
2. Update version release via admin API
3. If force update, set `forceUpdate: true`
4. Clients will be notified on next heartbeat

## Prohibited

- Do NOT expose private key files
- Do NOT use InMemory database in production
- Do NOT use default admin credentials (admin/admin123)
- Do NOT enable `/api/client/public-key` endpoint in production
- Do NOT commit .env files or keys to repository
- Do NOT expose JWT secret in source code
