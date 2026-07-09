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

## 在线更新系统

- 用户端支持检测新版本（VersionChecker v2）
- 用户端支持弹窗提示更新（UpdateDialog）
- 用户端支持下载更新包（UpdateDownloader）
- 用户端支持 manifest 签名校验（UpdateVerifier）
- 用户端支持 update zip sha256 校验
- 用户端支持 update_agent 替换文件
- 更新失败支持回滚
- 强制更新时不能跳过
- 下载过程有进度条（UpdateProgressDialog）
- 只允许 HTTPS 下载

## 发布流水线

- 已新增 release_publisher_ui.py（CustomTkinter GUI）
- 已新增 release_pipeline.py（CLI 一键发布）
- 已新增 build_release.bat
- 已新增 protect_csharp.ps1（混淆器接入占位）
- 已新增 generate_manifest.py / sign_manifest.py / verify_manifest.py
- 已新增 build_update_package.py（zip 打包）
- 已新增 check_release_package.py（源码/私钥泄露检查）
- 私钥不进入 git（.gitignore 已配置）
- 用户端只带 public key（resources/security/release_public.pem）

## 加密 / 混淆处理

- 发布 UI 有"加密/混淆处理"入口
- release 模式未配置混淆器会失败
- dev 模式允许跳过混淆但必须 WARNING
- 发布包会检查源码和私钥泄露

## 检查工具

- 已新增 check_update_system.py（21 项检查）
- 已通过 check_core_login_gate.py（27/27 PASS）
- 已通过 check_update_system.py（21/21 PASS）

## 在线更新真实闭环修复完成

- 主界面"检查更新"已改为签名更新系统
- 不再默认打开 GitHub Release / 浏览器下载
- UpdateDialog 的"立即更新"会调用 UpdateService
- 更新流程会下载 manifest.json / manifest.sig / update zip
- manifest 签名失败会拒绝更新
- zip sha256 失败会拒绝更新
- 解压后文件 hash 失败会拒绝更新
- UpdateAgent 替换后会按 manifest 再次校验
- 更新失败会回滚
- generate_manifest.py 不再把 zip / manifest / latest 写入 files
- update_verifier.py 已使用 safe_extract_zip 防 Zip-slip
- build_release.bat 已改为 version / private-key / obfuscator-path 三参数必填
- release_pipeline.py 已支持 --base-update-url
- release 模式下 protect_csharp.ps1 默认不能假混淆
- check_update_system.py 已通过 31/31 PASS
- check_core_login_gate.py 已通过 27/27 PASS
- dotnet build -c Release 已通过，0 errors, 0 warnings

## 在线更新最终收尾

- build_release.bat 已支持 base_update_url 第 4 参数
- build_release.bat 会把 --base-update-url 传给 release_pipeline.py
- release_pipeline.py 在 release 模式下没有 base-update-url 会失败
- start_auto_check 已改为优先使用签名更新系统
- start_auto_check 不再默认调用旧 GitHub Release 检查
- 未配置 update.latest_url 时自动检查静默跳过
- 手动"检查更新"仍会提示未配置 update.latest_url
- release_publisher_ui.py 已增加更新服务器 URL 输入框
- release_publisher_ui.py 一键发布会传 --base-update-url

## 发布中心可用性修复

- 发布中心已支持自动搜索项目路径
- 发布中心已支持自动搜索 dist / release 目录
- 发布中心已支持自动搜索 APPDATA 私钥
- 发布中心已支持自动搜索常见混淆器路径
- 发布中心已支持填充 v1.6.1-test 测试配置
- 发布中心已支持生成测试私钥到 APPDATA
- 发布中心已支持停止当前任务
- 发布中心长任务已有超时保护
- 私钥选择已改为文件选择
- 混淆器选择已改为 exe 文件选择
- dev 模式允许跳过混淆
- release 模式必须配置真实混淆器
