# Production Ready 验收报告

## 结果
条件通过 — 核心授权 E2E 验证通过，生产化改造进行中

## 分支
commercial-production-ready

## 已完成

### 1. 验收记录修正
- 已移除旧的测试绕过接口调用（原 license.save_ticket / license.reload）
- 验收表从"待验证"更新为真实状态
- 已通过检查：python compileall、dotnet build CoreService、dotnet build server、check_core_ipc、check_core_runtime、check_license_e2e

### 2. PostgreSQL 服务器配置
- AutoDoor.Infrastructure 引入 Npgsql.EntityFrameworkCore.PostgreSQL
- AutoDoor.Api Program.cs 根据 Database:Provider 选择 PostgreSQL 或 InMemory
- appsettings.json 增加 Database 配置节
- docker-compose.yml 增加 PostgreSQL 16 服务
- SeedData 区分 Development/Production 环境
- Production 环境通过环境变量创建初始 admin
- 保留 InMemory 作为 dev/test fallback

### 3. JWT Admin API
- 新增 `/api/admin/login` 返回真实 JWT token
- Admin CRUD 接口添加 `[Authorize]` 属性
- 使用 `Microsoft.AspNetCore.Identity.PasswordHasher` 存储密码 hash
- 不再使用固定 dev-jwt-token 和 HASHED:password 假 hash
- 保留 `/api/dev-admin` 仅限 Development 环境

### 4. 生产密钥管理
- Server TicketSigner 支持从环境变量 `AUTODOOR_SERVER_PRIVATE_KEY_PEM` / `AUTODOOR_SERVER_PRIVATE_KEY_PATH` 读取私钥
- Production 无私钥拒绝启动
- Development 生成临时 key 并写入日志
- `GetPrivateKeyPem()` 标记为 [Obsolete] dev-only
- `/api/client/public-key` 仅 Development 环境可用
- CoreService 支持从环境变量 / appsettings / 文件路径读取公钥

### 5. C# runtime 接入 UI
- RuntimeBridge 已实现 start_tree / pause_tree / resume_tree / stop_tree / status / logs / stats
- 内部调用 CoreService TCP IPC
- 设置管理器增加 runtime.use_csharp_core 配置项
- 默认 false，保持 Python runtime 兼容
- 新增 tools/check_ui_runtime_bridge.py 验证

### 6. C# ImageMatcher / OCR
- OcrService 实现 C# 调 Python OCR worker 子进程方案
- 新增 tools/ocr_worker.py
- ImageMatcher 保留 partial（OpenCvSharp4 引入失败时回退）

### 7. Runtime tick/logs
- RuntimeHost tick_count 每执行一个节点递增
- DelayNode 支持 delay_ms / duration_ms / seconds 字段
- LogStatusNode 写入 RuntimeHost logs
- runtime.logs 返回包含 Tree started / DelayNode executed / LogStatusNode 等信息

### 8. CI 自动验证
- 新增 GitHub Actions workflow：在 Windows runner 运行全部检查
- 触发条件：push 到 commercial-* 分支 + workflow_dispatch

## 已执行检查

| 命令 | 结果 | 备注 |
|---|---|---|
| python compileall | 通过 | 无语法错误 |
| dotnet build CoreService | 通过 | 0 errors, CA1416 warnings (Windows-only) |
| dotnet build server | 通过 | 0 errors |
| check_core_ipc | 通过 | core.hello + core.shutdown 正常 |
| check_core_runtime | 通过 | tree.start/stop/logs 正常 |
| check_license_e2e | 通过 | 完整激活链路 verified |
| check_ui_runtime_bridge | 通过 | runtime bridge 通过 TCP IPC 可用 |
| build_commercial | 未验证 | 需要完整 PyInstaller + dotnet publish 环境 |
| check_dist_no_source | 未验证 | 需要 dist 目录 |
| check_commercial_package | 未验证 | 需要 dist 目录 |
| check_built_app_smoke | 未验证 | 需要 dist 目录 |
| rg 旧绕过 action | 通过 | 零匹配 |
| rg 签名占位/弃用 API | 通过 | 零匹配 |
| rg 作者信息 | 通过 | 仅检查脚本正则中存在 |

## 仍未完成

1. 商业打包（build_commercial.bat + dist 检查）— 需完整 PyInstaller 环境
2. OCR / ImageMatcher C# 集成 — OcrService 实现 Python worker 桥接，ImageMatcher 使用 OpenCvSharp4（依赖系统安装）

## Partial 功能

1. ImageMatcher — 引入 OpenCvSharp4，若运行环境缺少 Visual C++ 运行时可能失败
2. OCUConditionNode — 通过 Python worker 子进程实现，延迟高于纯 C# 方案
3. C# runtime 节点兼容 — 当 C# runtime 返回 NODE_NOT_IMPLEMENTED 时 UI 提示切换回 Python

## 生产风险

1. PostgreSQL 依赖外部数据库服务，docker-compose 可缓解
2. JWT Secret 需生产环境配置强随机密钥
3. 私钥管理依赖环境变量或密钥分发系统
4. 商业打包未验证，发布流程未端到端确认
5. C# runtime 节点兼容性未全覆盖

## 下一步建议

1. 在 CI 环境运行 build_commercial.bat 验证商业打包
2. 部署 PostgreSQL 到生产服务器
3. 配置反向代理（Nginx）和 HTTPS
4. 完善 C# runtime 节点覆盖（ImageConditionNode / OcrConditionNode 完整实现）
5. 部署后进行完整 E2E 测试
