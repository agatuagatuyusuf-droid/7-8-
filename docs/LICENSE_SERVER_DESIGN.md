# 授权服务器设计

## 技术栈

- ASP.NET Core 8
- PostgreSQL
- Redis
- JWT 管理员登录
- Ed25519 / RSA 签名授权票据
- Docker 部署
- Nginx HTTPS

## 数据库表

- admins
- users
- products
- product_features
- licenses
- license_features
- machines
- activation_codes
- orders
- payments
- license_sessions
- version_releases
- audit_logs
- blacklist

## API 设计

### 客户端 API

| Method | Endpoint |
|--------|----------|
| POST | /api/client/activate |
| POST | /api/client/refresh |
| POST | /api/client/status |
| POST | /api/client/deactivate |
| POST | /api/client/heartbeat |
| GET | /api/client/version/latest |

### 管理员 API

| Method | Endpoint |
|--------|----------|
| POST | /api/admin/login |
| GET | /api/admin/dashboard |
| CRUD | /api/admin/users |
| CRUD | /api/admin/products |
| CRUD | /api/admin/licenses |
| CRUD | /api/admin/activation-codes |
| CRUD | /api/admin/machines |
| CRUD | /api/admin/orders |
| CRUD | /api/admin/version-releases |
| GET | /api/admin/audit-logs |

## 授权票据格式

服务器返回签名票据：

```json
{
  "ticket_version": 1,
  "product_id": "autodoor_pro",
  "license_id": "LIC-001",
  "user_id": "USER-001",
  "machine_code": "HASHED-MACHINE",
  "edition": "pro",
  "features": ["ocr", "image_match", "schedule"],
  "issued_at": "2027-07-08T00:00:00Z",
  "expire_at": "2028-07-08T00:00:00Z",
  "offline_until": "2027-07-11T00:00:00Z",
  "force_update_min_version": "1.6.0",
  "signature": "BASE64_SIGNATURE"
}
```

客户端只内置公钥。私钥只在服务器。
