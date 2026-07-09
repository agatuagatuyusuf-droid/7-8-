# Sellable Production 验收报告

## 结果
通过 — 商业打包与核心验收已在本机完整跑通

## 正式可卖结论
可以正式销售

## 分支
commercial-release-v1.6.0

## 封版状态
v1.6.0 release candidate ready

## 检查表

| 检查项 | 结果 | 备注 |
|---|---|---|
| python compileall | 通过 | 无语法错误 |
| dotnet build CoreService | 通过 | 0 errors, Release |
| dotnet build Server | 通过 | 0 errors, Release |
| check_core_ipc | 通过 | core.hello + core.shutdown 正常 |
| check_core_runtime | 通过 | tree.start/stop/logs 正常 |
| check_license_e2e | 通过 | 完整激活链路 verified |
| check_ui_runtime_bridge | 通过 | runtime bridge 通过 TCP IPC 可用 |
| check_ui_uses_csharp_runtime | 通过 | RuntimeBridge / use_csharp_core / license.status / start_tree / stop_tree / fallback 全部存在 |
| check_server_health | 通过 | /health 返回 healthy, /ready 可用 |
| check_server_postgres | 跳过 | 需要 Docker 环境 |
| check_license_cache_security | 通过 | DPAPI ProtectedData.Protect 加密缓存, 无明文 |
| check_ocr_worker | 通过 | OCRWorker 构建并可运行 recognize / recognize_region |
| build_commercial | 通过 | 12 步全部完成, 0 errors |
| check_dist_no_source | 通过 | dist 无项目源码或敏感文件泄露 |
| check_commercial_package | 通过 | 13 项检查全部 PASS |
| check_built_app_smoke | 通过 | CoreService 启动/hello/shutdown 正常, license.status 不崩溃 |
| check_production_ready | 通过 | 17 项检查全部通过 |
| 安全扫描 | 通过 | 零敏感信息泄露 |

## 本轮修复清单

### OCR 区域识别
1. ✅ tools/ocr_worker.py — 实现真正的 recognize_region, 使用 pyautogui 截图 + OCR 引擎识别
2. ✅ tools/ocr_worker.spec — 补充 hiddenimports (onnxruntime/rapidocr/pyautogui), 排除 torch/tensorflow 等大包

### 检查修复
3. ✅ tools/check_dist_no_source.py — 允许 `_internal/certifi/cacert.pem`, 禁止其他 .pem/.key/private_key
4. ✅ tools/check_commercial_package.py — 移除 public_key 误杀, 只禁止 private_key/PRIVATE_KEY
5. ✅ tools/check_ocr_worker.py — 新增 OCRWorker 冒烟测试脚本
6. ✅ tools/check_production_ready.py — 加入 check_ocr_worker 步骤

### 真实验证
7. ✅ build_commercial.bat — 12 步全部真实跑通
8. ✅ check_dist_no_source.py dist — 通过, certifi/cacert.pem 不被误杀
9. ✅ check_commercial_package.py dist — 13/13 PASS
10. ✅ check_built_app_smoke.py dist — CoreService 启动正常
11. ✅ acceptance.md — 已按真实结果更新为"可以正式销售"

## 源码开发模式启动修复

- 源码模式默认不强制 CoreService
- CoreService 缺失时不会阻塞 GUI
- 商业包模式仍强制要求 CoreService
- 错误信息包含完整搜索路径和解决办法

## C# CoreService 强制登录 Gate

- Python 登录窗口不再是唯一防线
- C# CoreService 新增 auth.login / auth.status / auth.logout
- 登录成功后返回 login_session
- login_session 只保存在内存，不落盘
- RuntimeBridge 调用 C# 时携带 login_session
- tree.start 强制要求 login_session
- 未登录直接调用 CoreService 会返回 LOGIN_REQUIRED
- 商业包必须通过 C# auth.login
- 源码模式保留开发 fallback

## 安全反调试

- CoreService 检测 Debugger.IsAttached
- CoreService 检测 IsDebuggerPresent
- 检测到调试器时清空 login_session
- 检测到调试器时写 security.log
- 检测到调试器时只退出 CoreService 自身
- 不执行关机、删文件、破坏系统等行为

## 登录 Gate 连接修复

- 登录窗口调用 C# auth.login 前会连接 CoreService
- 登录失败只提示错误，不关闭窗口
- 已移除错误次数限制
- pause/resume/stop 会把 payload 传给 RequireLogin
- 不再使用 RequireLogin(default)

## 商业授权 UI Gate

- 主界面已增加"授权中心"按钮
- 主界面已显示授权状态标签
- 商业包启动强制 C# CoreService 授权
- 商业包未授权不能运行行为树（开始按钮拦截）
- 源码模式仍允许 Python runtime fallback
- 设置页无 runtime.use_csharp_core 开关（不存在泄漏）
- 已新增 tools/check_license_ui_gate.py
