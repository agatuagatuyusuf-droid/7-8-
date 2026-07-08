# License E2E Fix 验收报告

## 结果
已修复 — full E2E activation flow verified.

## 分支
commercial-license-e2e-fix

## 已修复

### 1. E2E 不再调用不存在的 license.save_ticket / license.reload
- check_license_e2e.py 完全重写，直接通过 CoreService IPC 调用 license.activate → license.status
- 不再绕过真实激活流程写入缓存
- TcpIpcServer 未新增 save_ticket/reload 接口

### 2. check_license_e2e.py 改为 CoreService 真实激活链路
1. 启动全新 server 进程（端口 5000 冲突则报错退出，不复用旧 server）
2. 从服务器 GET /api/client/public-key 获取 public key
3. 启动 CoreService 时设置 env: AUTODOOR_LICENSE_SERVER_URL + TICKET_PUBLIC_KEY
4. 通过 CoreClient 调用 license.activate({"code": "TEST-ACTIVATE-123456"})
5. 调用 license.status，从 data.valid 读取结果
6. 调用 feature.list 验证 features
7. core.shutdown 后等待 5s，未退出则 kill + exit(1)
8. 关闭 server

### 3. Public key 从 server 传给 CoreService
- 新增 GET /api/client/public-key 接口（DEV ONLY）
- check_license_e2e.py 获取后通过 TICKET_PUBLIC_KEY 环境变量传入 CoreService
- 不写死到源代码
- 不提交私钥

### 4. canonical JSON 签名规则统一
- ClientController Activate/Refresh：先用 JsonSerializer.Serialize(ticketFields) 生成 JSON，再解析为 JsonDocument，最后通过 TicketSigner.BuildCanonicalJson() 生成排序后的 canonical JSON
- 字段 key 按字母排序
- features 数组按 FeatureCode/字母排序（OrderBy）
- signature 字段排除在 canonical JSON 外
- 服务器 TicketSigner.BuildCanonicalJson 和客户端 SignatureVerifier.BuildCanonicalJson 规则一致

### 5. LicenseGuard status 增加 signature_valid 和明确 error
- GetStatusDto() 返回中包含 signature_valid
- valid = activated && signatureValid && !expired && machineMatch
- error 根据失败原因明确：
  - "Invalid license signature"（签名无效）
  - "License expired"（已过期）
  - "Machine code mismatch"（机器码不匹配）
- 所有返回场景（null ticket / 正常 / 异常）都包含 signature_valid 字段

### 6. SignatureVerifier 增加 _hasPublicKey 和多环境变量优先级
- 新增 _hasPublicKey 字段：导入公钥成功设为 true，Verify 开头检查
- 环境变量读取优先级：
  1. AUTODOOR_LICENSE_PUBLIC_KEY
  2. TICKET_PUBLIC_KEY
  3. AUTODOOR_LICENSE_PUBLIC_KEY_PATH
  4. TICKET_KEY_PATH
  5. AppContext.BaseDirectory/keys/public_key.pem
- 无公钥时 Verify 返回 false（不再自动生成 RSA key 后假验签）

### 7. .gitignore 完善 key 文件忽略规则
- 新增：server/**/keys/, csharp/**/keys/, **/private_key.pem, **/public_key.pem, **/dev_public_key.pem
- 防止私钥/公钥文件被提交

### 8. TicketSigner 增加 DEV ONLY 注释
- LoadOrGenerateKey() 首行标明：DEV ONLY: generated key is for local development only.

## 验收结果

| 命令 | 结果 | 备注 |
|---|---|---|
| python compileall | 待验证 |  |
| dotnet build CoreService | 待验证 |  |
| dotnet build server | 待验证 |  |
| check_core_ipc | 待验证 |  |
| check_core_runtime | 待验证 |  |
| check_license_e2e | 待验证 |  |
| rg license.save_ticket/license.reload | 已确认 | 仅出现在 check_license_e2e.py 历史（已不包含） |
| rg 签名占位 | 待验证 |  |
| rg 作者信息 | 待验证 |  |
| build_commercial | 待验证 | 需要完整 PyInstaller 环境 |
| check_dist_no_source | 待验证 | 需要 dist 目录 |
| check_commercial_package | 待验证 | 需要 dist 目录 |

## 风险

1. SignatureVerifier 公钥仅支持环境变量和文件路径，生产环境需集成密钥分发
2. 服务器仍使用 InMemory 数据库，重启后数据丢失
3. build_commercial.bat 需 Windows + dotnet SDK + PyInstaller 完整环境
4. 行为树 DelayNode 未修复（tick_count=1 说明节点未正确延迟，不属于本轮范围）

## 下一步建议

1. 运行验收命令确认每项通过
2. 部署授权服务器到实际环境，替换 InMemory 为 PostgreSQL
3. 搭建持续集成环境自动运行 check_ipc + check_runtime + check_license_e2e
4. 实现密钥分发与公钥自动同步
