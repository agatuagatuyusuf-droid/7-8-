# 安全加固文档

## 已实现

| 措施 | 状态 | 说明 |
|---|---|---|
| RSA ticket 签名 | ✅ 已实现 | 服务器 RSA-2048 签名，C# 客户端验签 |
| C# 验签 | ✅ 已实现 | SignatureVerifier 验证所有 ticket |
| 机器码绑定 | ✅ 已实现 | 激活时绑定机器码，LicenseGuard 校验匹配 |
| DPAPI 授权缓存 | ✅ 已实现 | LicenseCache 使用 ProtectedData.Protect |
| Production 私钥强制配置 | ✅ 已实现 | Production 无私钥拒绝启动 |
| Production 禁止 InMemory | ✅ 已实现 | Production 必须 PostgreSQL |
| Admin JWT | ✅ 已实现 | JWT Bearer 认证，角色授权 |
| 审计日志 | ✅ 已实现 | AdminAuditService 记录写操作 |
| 激活码安全生成 | ✅ 已实现 | ActivationCodeGenerator 使用 CSPRNG |

## 预留（未启用）

| 措施 | 状态 | 说明 |
|---|---|---|
| C# 混淆 | ⏳ 预留 | 使用 Obfuscar 或 ConfuserEx |
| 加壳 | ⏳ 预留 | 使用 Themida / Enigma |
| 代码签名 | ⏳ 预留 | 需要代码签名证书 |
| PyArmor | ⏳ 预留 | 保护 Python 代码 |
| 商业证书签名 | ⏳ 预留 | 需要 Authenticode 证书 |
| 高级反调试 | ⏳ 预留 | IsDebuggerPresent 等检测 |

## 安全建议

1. 生产环境禁用 `/api/client/public-key` 接口
2. 定期轮换 JWT Secret 和 RSA 密钥对
3. PostgreSQL 仅允许 API 服务器访问
4. 所有 API 使用 HTTPS
5. 管理员页面限制 IP 白名单
