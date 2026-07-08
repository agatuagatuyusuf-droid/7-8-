# AutoDoor License Server

授权服务器后台，提供激活码管理、授权票据签发、机器绑定、版本控制等功能。

## 技术栈

- ASP.NET Core 8
- Entity Framework Core (InMemory / SQLite / PostgreSQL)
- RSA-SHA256 票据签名
- JWT 管理员登录
- Swagger API 文档
- Docker Compose

## 快速开始

```bash
cd server/AutoDoor.Server
dotnet run --project src/AutoDoor.Api
```

服务器默认监听 http://localhost:5000

## 测试激活码

`TEST-ACTIVATE-123456`

## 管理员登录

POST /api/admin/login
```json
{ "username": "admin", "password": "admin123" }
```

## 注意

- 当前使用 InMemory 数据库，重启数据丢失
- 私钥在启动时临时生成，不可用于生产
- 正式使用前必须配置 PostgreSQL 和真实 RSA 密钥
