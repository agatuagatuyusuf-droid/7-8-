# Handoff — commercial-p10-p15-fix

## 修复完成 (12 项)

| # | 修复内容 | 状态 |
|---|---------|------|
| 1 | core.shutdown 优雅退出 | ✅ 实测通过 |
| 2 | CoreService 打包路径 | ✅ |
| 3 | JSON 字段映射 | ✅ |
| 4 | RSA-SHA256 验签 | ✅ |
| 5 | LicenseGuard valid | ✅ |
| 6 | TicketSigner 密钥 | ✅ |
| 7 | check_core_runtime 断言 | ✅ 实测通过 |
| 8 | Image/OCR 异常 | ✅ |
| 9 | SendInput | ✅ |
| 10 | Admin API 安全 | ✅ |
| 11 | check_license_e2e | ✅ 脚本就绪 |
| 12 | 文档 | ✅ |

## 验收结果

- python compileall: ✅ 通过
- dotnet build CoreService: ✅ 0 errors, 14 warnings
- check_core_ipc: ✅ 通过
- check_core_runtime: ✅ 通过
- dotnet build server: ✅ 0 errors, 1 warning
- check_license_e2e: ⏳ 未验证（需双进程环境）
- build_commercial: ⏳ 未验证（需 PyInstaller）
- rg 作者信息: ✅ 无泄露

## 仍存在的问题

1. 行为树运行时 DelayNode 未正确执行（status=failed, elapsed_ms=0）
2. 运行时日志 message 为 null（序列化问题）
3. E2E 激活测试未实际跑通

## 风险

1. SignatureVerifier 需要公钥配置，生产需密钥分发机制
2. Admin API 为 /api/dev-admin，不可公网部署
3. 服务器 InMemory DB 生产需换 PostgreSQL
4. build_commercial 需要完整 Windows 构建环境

## 验收命令

```bash
python -m compileall main.py bt_core bt_gui bt_nodes bt_utils config bt_bridge
dotnet build csharp/AutoDoor.CoreService/src/AutoDoor.CoreService/AutoDoor.CoreService.csproj -c Release
python tools/check_core_ipc.py
python tools/check_core_runtime.py
dotnet build server/AutoDoor.Server/src/AutoDoor.Api/AutoDoor.Api.csproj -c Release
rg -n "wdhq4261761|298117299|QQ群|B站|bilibili|space.bilibili.com|my.feishu.cn" -g "*.py" -g "*.cs" -g "*.md" -g "*.json"
```
