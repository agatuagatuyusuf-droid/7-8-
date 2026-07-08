# Progress

## P10-P15 修复 (commercial-p10-p15-fix)
- [x] 1. core.shutdown 优雅退出 — CoreServiceLifetime + CancellationToken
- [x] 2. CoreService 打包路径 — 6 级优先级搜索
- [x] 3. JSON 字段映射 — [JsonPropertyName] + 空值校验
- [x] 4. RSA-SHA256 验签 — SignatureVerifier 真实实现
- [x] 5. LicenseGuard valid — 真实验签不再写死
- [x] 6. TicketSigner 稳定密钥 — env/file/自动生成
- [x] 7. check_core_runtime 真断言 — poll completed=true
- [x] 8. Image/OCR 不静默失败 — throw NotImplementedException
- [x] 9. SendInput — 替换已弃用 API
- [x] 10. Admin API 安全 — /api/dev-admin
- [x] 11. check_license_e2e.py — E2E 测试脚本
- [x] 12. 文档更新 — COMMERCIAL_BUILD.md + .goal/*
