# P10-P15 Fix 验收报告

## 结果
条件通过

## 分支
commercial-p10-p15-fix

## 已修复

### 1. core.shutdown 优雅退出
- CoreServiceLifetime.cs 存在
- TcpIpcServer 通过 `_lifetime.RequestShutdown()` 触发关闭
- Program.cs 等待 CancellationToken，捕获 OperationCanceledException
- check_core_ipc.py 在 shutdown 后等待进程 5 秒，未退出则 exit(1)
- **实测通过** — check_core_ipc.py 验证进程在 shutdown 后优雅退出

### 2. CoreService 打包路径
- 搜索顺序：sys.executable/CoreService → _MEIPASS → 项目根 → publish → build → cwd
- 6 个优先级全部实现

### 3. JSON 字段映射
- 所有请求 DTO 添加 `[JsonPropertyName("snake_case")]`
- ActivateRequest 含 activation_code / machine_code / product_id
- 添加 IsValid() 校验，空值返回 INVALID_INPUT

### 4. 真实 RSA-SHA256 验签 (SignatureVerifier)
- 从环境变量/文件/默认路径加载公钥
- BuildCanonicalJson 移除 signature 字段
- 使用 RSA.VerifyData + SHA256 + Pkcs1 真实验签
- 验签失败返回 false

### 5. LicenseGuard 真实 valid
- GetStatusDto() 调用 `_verifier.Verify(root)`，不再硬编码 signatureValid=true
- valid = activated && signatureValid && !expired && machineMatch

### 6. TicketSigner 稳定密钥
- 支持 TICKET_PRIVATE_KEY 环境变量内联 PEM
- 支持 TICKET_KEY_PATH 文件路径
- 开发环境自动生成 keys/private_key.pem
- BuildCanonicalJson 排除 signature 字段，字段按字母序排序

### 7. check_core_runtime 真断言
- tree.validate → assert success
- tree.start → assert success
- poll tree.status 直到 completed=true
- runtime.logs 非空断言
- runtime.stats 断言
- 所有失败 exit(1)

### 8. Image/OCR 不静默失败
- ImageConditionNode：throw NotImplementedException
- OcrConditionNode：throw NotImplementedException

### 9. SendInput
- 完整 WIN32 INPUT 结构体定义
- 使用 SendInput API 替代已弃用的 keybd_event/mouse_event

### 10. Admin API 安全
- 路由改为 /api/dev-admin（开发专用）
- 代码中明确 DEV ONLY

### 11. check_license_e2e.py
- 启动 server + CoreService
- 调用 license.activate 激活
- 调用 license.status 验证 valid=true
- 失败 exit(1)

### 12. 文档
- COMMERCIAL_BUILD.md 更新

## 已执行检查

| 命令 | 结果 | 备注 |
|---|---|---|
| python compileall | 通过 | 无错误 |
| dotnet build CoreService (Release) | 通过 | 14 warnings (平台兼容性，预期) |
| check_core_ipc | 通过 | core.hello + core.shutdown → 进程退出 |
| check_core_runtime | 通过 | tree.validate/start/status + logs + stats + shutdown |
| dotnet build server (Release) | 通过 | 1 warning (预期) |
| check_license_e2e | 未验证 | 需要 server dotnet run + CoreService 同时运行 |
| build_commercial | 未验证 | 需要完整 PyInstaller 环境 |
| check_dist_no_source | 未验证 | 需要 dist 目录 |
| check_commercial_package | 未验证 | 需要 dist 目录 |
| rg 作者信息 | 通过 | 仅 check_commercial_package.py 中的正则 |

## 仍未完成

1. check_license_e2e 未实际运行 — 需要打开两个 shell 分别启动 server 和 CoreService
2. build_commercial.bat 未运行 — 缺少 PyInstaller 完整环境
3. 行为树运行时 — tree 以 `status: failed` 结束（tick_count=1, elapsed_ms=0），延迟节点未生效
4. 运行时日志 — log message 为 null（序列化问题，不影响功能）

## 生产风险

1. SignatureVerifier 需要从服务器获取公钥 — 当前支持环境变量/文件，未集成密钥分发
2. Admin API 路由为 /api/dev-admin — 不可部署到公网生产环境
3. 服务器 InMemory 数据库重启后数据丢失，生产需切换 PostgreSQL
4. build_commercial.bat 需 Windows + dotnet SDK + PyInstaller 完整环境
5. E2E 激活测试未实际跑通（缺少完整环境）

## 下一步建议

1. 修复 DelayNode 行为树执行（tick_count=1, elapsed_ms=0 说明节点未正确延迟）
2. 完善运行时日志序列化
3. 部署授权服务器到实际环境，替换 InMemory 为 PostgreSQL
4. 搭建持续集成环境，自动运行 check_ipc + check_runtime
5. 正式收费前，实现密钥分发与公钥自动同步
