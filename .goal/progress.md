# Progress

## P0-P9 阻塞修复
- [x] TCP IPC (TcpIpcServer + CoreClient with TCP sockets)
- [x] CoreService packaging (build_commercial.bat with dotnet publish + copy)
- [x] license.status 增加 valid 字段 (LicenseGuard.GetStatusDto)
- [x] LicenseClient 配置化 (appsettings.json + env vars)
- [x] GitHub Actions 禁用自动发布
- [x] .gitignore 更新 (.goal/state.json 允许提交)

## P10 UI 激活窗口
- [x] bt_bridge/license_session.py - LicenseSession 生命周期管理
- [x] bt_gui/dialogs/activation_dialog.py - CustomTkinter 模态激活窗口
- [x] main.py - 集成授权检查流程

## P11 C# 行为树运行时
- [x] RuntimeHost, RuntimeContext, RuntimeState
- [x] BehaviorTreeEngine, NodeBase, NodeStatus, NodeRegistry, Blackboard, TreeSerializer
- [x] tree.validate, tree.start, tree.pause, tree.resume, tree.stop, tree.status
- [x] runtime.logs, runtime.stats

## P12 核心节点迁移
- [x] StartNode, SequenceNode, SelectorNode (Composite)
- [x] DelayNode, LogStatusNode, SetVariableNode (Actions)
- [x] VariableConditionNode (Conditions)
- [x] KeyPressNode, MouseClickNode, TextInputNode (partial)

## P13 OCR / 图像 / 输入
- [x] InputController (SendInput native)
- [x] ScreenshotService, ColorDetector
- [x] ImageMatcher (partial - not implemented)
- [x] OcrService (partial - not implemented)
- [x] ColorConditionNode (usable)
- [x] ImageConditionNode (partial - returns Failure)
- [x] OcrConditionNode (partial - returns Failure)

## P14 授权服务器后台
- [x] ASP.NET Core 8 project structure (Api / Domain / Infrastructure)
- [x] 完整数据模型 (17 entities)
- [x] Client API: activate, refresh, status, deactivate, heartbeat, version
- [x] Admin API: login, dashboard, CRUD for all entities
- [x] RSA-SHA256 签名 (TicketSigner)
- [x] InMemory database + seed data
- [x] 测试激活码 TEST-ACTIVATE-123456
- [x] Docker Compose support
- [x] Swagger API docs

## P15 商业打包
- [x] build_commercial.bat updated (9 steps)
- [x] tools/copy_core_service_to_dist.py
- [x] tools/copy_notices_to_dist.py
- [x] tools/check_commercial_package.py
- [x] tools/check_core_ipc.py
- [x] tools/check_core_runtime.py
