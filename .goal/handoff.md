# Handoff

## 当前完成 (P0-P8)
- ✅ 品牌配置集中化（brand.json + brand_manager.py）
- ✅ 原作者公共信息清理（wdhq4261761, QQ群, B站, feishu 全部清理）
- ✅ README 商业版重写
- ✅ PyInstaller 源码泄露修复（commercial spec）
- ✅ 商业构建脚本（build_commercial.bat）
- ✅ 第三方许可证文件
- ✅ 授权客户端设计文档
- ✅ C# CoreService 骨架（完整 License 模块 + IPC 服务器）
- ✅ Python bridge 骨架（core_process, core_client, license_bridge, runtime_bridge）

## 已修改的文件
- README.md, build_config.json, generate_build_info.py, main.py
- bt_utils/version_checker.py, bt_utils/brand_manager.py
- config/settings_manager.py, config/brand.json
- bt_gui/app.py, bt_gui/bt_editor/editor.py
- doc/用户使用手册.md, doc/AI_Tree_Generator_Prompt.md, doc/01_架构文档.md, doc/02_详细实现方法.md
- docs/build_config_guide.md, 使用说明.txt
- .github/workflows/build.yml
- autodoor_bt_commercial.spec, build.bat

## 新增文件
- config/brand.json, bt_utils/brand_manager.py
- legal/README.md, legal/.gitignore
- NOTICE.txt, THIRD_PARTY_LICENSES.txt
- tools/check_dist_no_source.py, tools/generate_third_party_licenses.py
- build_commercial.bat, requirements-build.txt
- docs/CORE_IPC_PROTOCOL.md, docs/LICENSE_SERVER_DESIGN.md, docs/COMMERCIAL_BUILD.md
- csharp/AutoDoor.CoreService/（完整 C# 项目骨架）
- bt_bridge/（Python IPC 桥接模块）
- .goal/（进度文件）

## 剩余任务
- ⏳ P10: UI 激活窗口（需要设计激活弹窗）
- ⏳ P11-P15: 行为树运行时迁移、节点迁移、OCR/图像/输入迁移、服务器后台

## 风险
1. C# CoreService 需要 .NET 8 SDK 才能编译
2. PyInstaller 构建需要先运行 generate_build_info.py
3. 旧用户数据目录 autodoor_behavior_tree 需要兼容迁移

## 验收命令
```
python -m compileall main.py bt_core bt_gui bt_nodes bt_utils config
rg -n "wdhq4261761|298117299|QQ群|B站|bilibili|space.bilibili.com|my.feishu.cn|autodoor_behavior_tree" .
build_commercial.bat
python tools/check_dist_no_source.py dist
```
