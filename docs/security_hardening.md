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

## C# CoreService 强制登录 Gate

已实现：

- Python 登录窗口不是唯一防线
- C# CoreService 新增 auth.login / auth.status / auth.logout
- 登录成功后 C# 返回内存态 login_session
- RuntimeBridge 调用 C# tree.start 时携带 login_session
- C# tree.start 强制 RequireLogin
- 未登录直接调用 C# tree.start 会返回 LOGIN_REQUIRED
- 商业包模式必须通过 C# auth.login
- 源码模式允许本地登录 fallback，但仅用于开发

## 安全反调试边界

已实现：

- CoreService 启动检测 Debugger.IsAttached
- CoreService 调用 Windows IsDebuggerPresent
- 检测到调试器时清空 login_session
- 检测到调试器时写 security.log
- 检测到调试器时只退出 CoreService 自身

明确不做：

- 不关机
- 不蓝屏
- 不删除用户文件
- 不破坏系统
- 不执行任何攻击性行为

后续增强：

- C# 混淆
- 代码签名
- Authenticode 校验
- 完整 hash manifest
- 服务器 security-event 上报
- 多次风险事件自动封禁机器码

## 安全建议

1. 生产环境禁用 `/api/client/public-key` 接口
2. 定期轮换 JWT Secret 和 RSA 密钥对
3. PostgreSQL 仅允许 API 服务器访问
4. 所有 API 使用 HTTPS
5. 管理员页面限制 IP 白名单
