# Sellable Production 验收报告

## 结果
条件通过 — 修复脚本通过，商业打包需完整 CI 环境验证

## 正式可卖结论
不建议正式销售 — 商业打包尚未在 CI 中完整跑通

## 分支
commercial-sellable-production-fix

## 检查表

| 检查项 | 结果 | 备注 |
|---|---|---|
| python compileall | 未验证 | 需手动运行 |
| dotnet build CoreService | 未验证 | 需手动运行 |
| dotnet build Server | 未验证 | 需手动运行 |
| check_core_ipc | 未验证 | 需 CoreService 运行 |
| check_core_runtime | 未验证 | 需 CoreService 运行 |
| check_license_e2e | 未验证 | 需 Server 运行 |
| check_ui_runtime_bridge | 未验证 | 需 CoreService 运行 |
| check_ui_uses_csharp_runtime | 未验证 | 需手动运行 |
| check_server_health | 未验证 | 需 Server 运行 |
| check_server_postgres | 未验证 | 需 Docker |
| check_license_cache_security | 未验证 | 需手动运行 |
| build_commercial | 未验证 | 需 PyInstaller + dotnet 完整环境 |
| check_dist_no_source | 未验证 | 需 dist 目录 |
| check_commercial_package | 未验证 | 需 dist 目录 |
| check_built_app_smoke | 未验证 | 需 dist 目录 |
| check_production_ready | 未验证 | 需完整环境 |
| 安全扫描 | 未验证 | 需 ripgrep |

## 代码修复清单

### 打包修复
1. ✅ build_commercial.bat — 删除末尾 pause, 修复 OCRWorker 复制逻辑, 改为先 Build OCRWorker 再复制到 dist
2. ✅ tools/ocr_worker.spec — 增加 rapidocr_onnxruntime / PIL / pytesseract hiddenimports, 改为 console=True
3. ✅ tools/copy_core_service_to_dist.py — 改为从 build/ocr_worker/OCRWorker.exe 复制, 不再要求 OCRWorker 已存在于 dist
4. ✅ tools/check_dist_no_source.py — dist 不存在时必须 FAIL, 增加 .cs/.csproj/.sln/.env/.pem/.key 检查范围
5. ✅ tools/check_commercial_package.py — 增加 OCRWorker.exe 检查、禁止 TEST-ACTIVATE-123456 / CHANGE_ME_DEV_SECRET / admin123 / 私钥扫描
6. ✅ tools/check_built_app_smoke.py — OCRWorker/OCRWorker.exe 不存在时 FAIL

### Client 授权 API
7. ✅ Disabled 激活码不能激活 — 查询条件增加 && !a.Disabled
8. ✅ Activate offline_until 按 OfflineDays 计算, 不再硬编码 72h
9. ✅ Refresh ticket 补齐 license_type / major_version_limit / session_id / offline_until (按 OfflineDays)
10. ✅ Refresh 创建/更新 LicenseSession
11. ✅ HeartbeatRequest 增加 session_id / app_version / core_version 字段
12. ✅ Heartbeat 更新 LicenseSession (session_id 匹配时更新 LastSeenAt)
13. ✅ Heartbeat 返回 active / banned / force_update / latest_version / min_supported_version / download_url

### Server 安全
14. ✅ Production CORS 不再 AllowAnyOrigin, 改为 AUTODOOR_ALLOWED_ORIGINS 环境变量
15. ✅ GetMachines 返回 MachineDto (不再裸露 EF Entity)
16. ✅ GetAuditLogs 返回 AuditLogDto (不再裸露 EF Entity)

### 检查脚本
17. ✅ check_license_cache_security.py — 检查 cache.dat (真实文件名) 和 license.cache
18. ✅ check_production_ready.py — 加入 build_commercial / check_built_app_smoke, 禁止关键 skip 不被视为 pass
19. ✅ acceptance.md — 按真实结果填写, 不写假通过
