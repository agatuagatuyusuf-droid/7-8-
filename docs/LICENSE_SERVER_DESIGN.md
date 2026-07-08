# 授权服务器设计

## 技术栈

- ASP.NET Core 8
- Entity Framework Core
- InMemory / SQLite / PostgreSQL（可配置）
- RSA-SHA256 签名授权票据
- JWT 管理员登录
- Swagger API 文档
- Docker Compose

## 项目结构

```
server/AutoDoor.Server/
├── AutoDoor.Server.sln
├── docker-compose.yml
├── Dockerfile
├── README.md
├── docs/
└── src/
    ├── AutoDoor.Api/         # Web API + Controllers
    ├── AutoDoor.Domain/      # 实体模型
    └── AutoDoor.Infrastructure/  # DbContext + 签名
```

## 数据模型

- Admin（管理员）
- User（用户）
- Product（产品）
- Feature（功能特性）
- License（授权许可）
- LicenseFeature（许可功能关联）
- Machine（绑定机器）
- ActivationCode（激活码）
- Order（订单）
- LicenseSession（会话）
- VersionRelease（版本发布）
- AuditLog（审计日志）

## API 设计

### 客户端 API

| Method | Endpoint | 说明 |
|--------|----------|------|
| POST | /api/client/activate | 激活码激活 |
| POST | /api/client/refresh | 刷新授权 |
| POST | /api/client/status | 查询授权状态 |
| POST | /api/client/deactivate | 解除授权 |
| POST | /api/client/heartbeat | 心跳 |
| GET | /api/client/version/latest | 最新版本 |

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
| CRUD | /api/admin/version-releases |
| GET | /api/admin/audit-logs |

## 授权票据格式

```json
{
  "ticket_version": 1,
  "product_id": "autodoor_pro",
  "license_id": "LIC-001",
  "user_id": "USER-001",
  "machine_code": "HASHED-MACHINE",
  "edition": "pro",
  "features": ["basic_editor", "basic_input", "schedule", "ocr", "image_match"],
  "issued_at": "2027-07-08T00:00:00Z",
  "expire_at": "2028-07-08T00:00:00Z",
  "offline_until": "2027-07-11T00:00:00Z",
  "force_update_min_version": "1.6.0",
  "signature": "BASE64_SIGNATURE"
}
```

## 机器码

基于 Windows 硬件信息的 SHA256 哈希：
- MachineGuid（注册表）
- CPU 名称
- 磁盘序列号
- 用户名 + 机器名

## 离线宽限

默认 72 小时离线宽限（可在 appsettings.json 配置）。

## RSA 签名

- 算法: RSA-SHA256（PKCS#1 v1.5）
- 服务器持有私钥，客户端只存公钥
- 签名时去掉 signature 字段，对 canonical JSON 签名
- 客户端验证签名后才接受票据

## 当前实现状态

- 服务器 TicketSigner：已完成，启动时生成临时 RSA 2048 密钥对
- 客户端 SignatureVerifier：占位实现，仅检查签名长度 > 0
- 不能用于正式收费授权

## 未完成风险

1. **SignatureVerifier 为占位实现**，不能用于正式收费授权。正式收费前必须实现真实 RSA/Ed25519 验签
2. 当前使用 InMemory 数据库，重启后数据丢失
3. 私钥不在仓库中保存，服务器启动时生成临时密钥，不可用于生产
4. 正式使用必须：
   - 配置 PostgreSQL
   - 生成并安全存储 RSA 私钥
   - 实现真实签名验证
   - 添加 HTTPS
   - 添加速率限制

## 私钥管理

- 私钥绝对不能提交进仓库
- .gitignore 已包含 `server/**/private*.pem` 和 `server/**/private*.key`
- 开发环境启动时生成临时密钥
- 生产环境通过环境变量或挂载卷注入私钥
