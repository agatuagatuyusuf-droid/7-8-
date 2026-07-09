# AutoDoor Pro 生产部署文档

## 系统要求

- **服务器**: Linux (Ubuntu 22.04+) / Windows Server 2019+
- **数据库**: PostgreSQL 16+
- **运行时**: .NET 8.0 Runtime
- **反向代理**: Nginx (推荐)

## 部署步骤

### 1. 环境变量配置

复制 `server/AutoDoor.Server/.env.example` 到 `.env` 并修改：

```
ASPNETCORE_ENVIRONMENT=Production
AUTODOOR_DB_PROVIDER=PostgreSQL
AUTODOOR_DB_CONNECTION_STRING=Host=postgres;Port=5432;Database=autodoor;Username=autodoor;Password=你的密码
AUTODOOR_SERVER_PRIVATE_KEY_PATH=/run/secrets/autodoor_private_key.pem
AUTODOOR_JWT_SECRET=你的64位随机字符串
AUTODOOR_ADMIN_USERNAME=admin
AUTODOOR_ADMIN_PASSWORD=你的管理员密码
License__ExposePublicKeyEndpoint=false
```

### 2. 数据库

PostgreSQL 自动创建表结构，首次启动时通过 EF Core 迁移初始化。

### 3. 生成密钥

```bash
openssl genrsa -out private_key.pem 2048
openssl rsa -in private_key.pem -pubout -out public_key.pem
```

### 4. Docker Compose 部署

```bash
cd server/AutoDoor.Server
docker compose up -d
```

### 5. 验证部署

- `GET /health` — 返回 `{"success":true,"status":"healthy"}`
- `GET /ready` — 返回 `{"success":true,"database":true,"signing_key":true}`

## 生产注意事项

1. JWT Secret 必须使用 64 位以上随机字符
2. 私钥文件权限必须为 600
3. PostgreSQL 必须配置密码认证
4. Nginx 必须配置 HTTPS
5. 定期备份 PostgreSQL 数据库
