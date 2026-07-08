# 商业构建文档

## 构建环境要求

1. Python 3.12 + 所有项目依赖
2. .NET 8 SDK（用于编译 CoreService）
3. PyInstaller（用于打包 Python UI）

## 构建流程

```bash
build_commercial.bat
```

流程：

1. 清理旧的 build/dist 目录
2. 从 build_config.json 生成构建信息
3. Python 语法检查 (compileall)
4. 构建 C# CoreService（dotnet build）
5. 发布 C# CoreService（dotnet publish）
6. PyInstaller 打包 (autodoor_bt_commercial.spec)
7. 复制 CoreService 到 dist（tools/copy_core_service_to_dist.py）
8. 复制法律声明文件（tools/copy_notices_to_dist.py）
9. 验证包完整性（check_dist_no_source + check_commercial_package）

## 构建产物

```
dist/autodoor-pro-{VERSION}/
  autodoor-pro-{VERSION}.exe       # 主程序
  CoreService/
    AutoDoor.CoreService.exe       # 授权服务
    AutoDoor.CoreService.dll
    appsettings.json               # 授权服务配置
    其他依赖文件
  assets/
  drivers/
  config/
  NOTICE.txt
  THIRD_PARTY_LICENSES.txt
```

## CoreService 位置

CoreService（AutoDoor.CoreService.exe）位于 `dist/autodoor-pro-{VERSION}/CoreService/` 目录。
主程序启动时会自动查找并启动 CoreService。

## 确认无源码泄露

构建后运行：
```bash
python tools/check_dist_no_source.py dist
python tools/check_commercial_package.py dist
```

## GitHub Actions

商业包请在 Windows 本地执行 `build_commercial.bat` 构建。
GitHub Actions 暂不自动发布商业包，避免误发布未授权版本。

## 注意事项

1. build_commercial.bat 依赖 .NET 8 SDK，确保 `dotnet` 命令可用
2. autodoor_bt_commercial.spec 不包含源码 .py 作为 datas
3. 构建前确保已执行 `generate_build_info.py`
4. 构建后运行 `tools/check_commercial_package.py` 验证完整性

## 打包工具依赖

```
pip install pyinstaller
```
