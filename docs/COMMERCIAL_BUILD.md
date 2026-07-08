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

查找优先级：
1. PyInstaller bundle 目录 /CoreService/（sys.frozen → os.path.dirname(sys.executable)）
2. PyInstaller _MEIPASS /CoreService/
3. 项目根目录 /CoreService/
4. C# dotnet publish 输出目录
5. C# dotnet build 输出目录
6. 当前工作目录 /CoreService/

## 密钥管理

服务器 RSA 密钥对存储在 `keys/` 目录：
- `keys/private_key.pem` — 服务器签名私钥
- `keys/public_key.pem` — CoreService 验证公钥

环境变量覆盖：
- `TICKET_PRIVATE_KEY` — 内联 PEM 私钥
- `TICKET_PUBLIC_KEY` — 内联 PEM 公钥
- `TICKET_KEY_PATH` — PEM 密钥文件路径

## 验证脚本

```bash
python tools/check_core_ipc.py       # TCP IPC 通信 + 优雅退出
python tools/check_core_runtime.py   # 行为树运行时执行 + 断言
python tools/check_license_e2e.py    # 端到端激活测试（服务器→CoreService→验证）
python tools/check_dist_no_source.py dist
python tools/check_commercial_package.py dist
```

## 修复内容 (commercial-p10-p15-fix)

1. **core.shutdown 优雅退出** — CoreServiceLifetime + CancellationToken 驱动，TcpIpcServer 通过 RequestShutdown() 退出
2. **CoreService 路径查找** — 新增 PyInstaller bundle 目录优先级
3. **JSON 字段映射** — 服务器 DTO 添加 [JsonPropertyName("snake_case")]
4. **RSA-SHA256 签名验证** — SignatureVerifier 真实验证，LicenseGuard.valid 依赖验证结果
5. **TicketSigner** — 稳定密钥加载（env/file），规范 JSON 排序后签名
6. **行为树断言** — check_core_runtime.py 真实断言 completed=true
7. **未实现节点** — ImageConditionNode/OcrConditionNode 抛出 NotImplementedException
8. **SendInput** — 替换已弃用的 keybd_event/mouse_event
9. **管理后台** — 路由改为 /api/dev-admin（开发专用）
10. **端到端测试** — 新增 check_license_e2e.py（激活→缓存→验证→退出）

## GitHub Actions

商业包请在 Windows 本地执行 `build_commercial.bat` 构建。
GitHub Actions 暂不自动发布商业包，避免误发布未授权版本。

## 注意事项

1. build_commercial.bat 依赖 .NET 8 SDK，确保 `dotnet` 命令可用
2. autodoor_bt_commercial.spec 不包含源码 .py 作为 datas
3. 构建前确保已执行 `generate_build_info.py`
4. 构建后运行 `tools/check_commercial_package.py` 验证完整性
5. 首次运行 `dotnet run --project server/.../AutoDoor.Api.csproj` 会自动生成 `keys/private_key.pem`

## 打包工具依赖

```
pip install pyinstaller
```
