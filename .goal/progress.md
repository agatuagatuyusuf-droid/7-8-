# Progress

## Phase 0: 初始化和状态文件
- [x] 创建 .goal/ 目录
- [x] state.json
- [x] progress.md
- [x] acceptance.md
- [x] handoff.md

## Phase 1: 品牌配置集中化
- [x] config/brand.json
- [x] bt_utils/brand_manager.py

## Phase 2: 原作者公共信息清理
- [x] README.md 重写（商业版）
- [x] main.py 清理（LOG_DIR, load_github_info）
- [x] build_config.json 清理（移除 wdhq、feishu）
- [x] generate_build_info.py 清理（使用 brand_manager）
- [x] bt_utils/version_checker.py 清理（移除 feishu 硬编码）
- [x] config/settings_manager.py 清理（目录路径改为 AutoDoorPro）
- [x] bt_gui/app.py 清理（标题）
- [x] bt_gui/bt_editor/editor.py 清理（数据目录）
- [x] doc/ 清理（用户手册、架构文档、AI Prompt）
- [x] docs/build_config_guide.md 清理
- [x] 使用说明.txt 清理
- [x] .github/workflows/build.yml 清理

## Phase 3: PyInstaller 源码泄露修复
- [x] autodoor_bt_commercial.spec（不包含 .py 源码作为 datas）
- [x] tools/check_dist_no_source.py

## Phase 4: 商业构建脚本
- [x] build_commercial.bat
- [x] requirements-build.txt

## Phase 5: 第三方许可证文件
- [x] NOTICE.txt
- [x] THIRD_PARTY_LICENSES.txt
- [x] tools/generate_third_party_licenses.py

## Phase 6: 文档
- [x] docs/LICENSE_SERVER_DESIGN.md
- [x] docs/CORE_IPC_PROTOCOL.md
- [x] docs/COMMERCIAL_BUILD.md
- [x] legal/README.md + .gitignore

## Phase 7: C# CoreService 骨架
- [x] 项目结构
- [x] Solution + 项目文件
- [x] Program.cs
- [x] IpcServer
- [x] LicenseClient, LicenseGuard, LicenseCache, SignatureVerifier
- [x] MachineCodeProvider, FeatureGate, LicenseTicket, LicenseState
- [x] build_core.bat

## Phase 8: Python bridge 骨架
- [x] bt_bridge/__init__.py
- [x] ipc_protocol.py
- [x] core_process.py
- [x] core_client.py
- [x] license_bridge.py
- [x] runtime_bridge.py

## Phase 9: 授权系统
- [x] C# 授权客户端（激活、刷新、状态、缓存、签名验证）
- [x] 功能权限控制（FeatureGate）
- [ ] UI 激活窗口

## Phase 10: UI 激活窗口
- [ ] 待开发
