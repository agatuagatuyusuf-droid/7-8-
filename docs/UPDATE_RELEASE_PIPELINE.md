# AutoDoor Pro 发布流水线说明

## 概述

本文档说明如何配置和使用 AutoDoor Pro 的发布流水线。

## 前置条件

- Python 3.11+
- .NET 8 SDK
- PyInstaller（打包用）
- 可选：C# 混淆器（如 ConfuserEx、Obfuscar）

## 私钥配置

1. 生成 RSA-2048 密钥对：

```bash
python -c "
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os

key = rsa.generate_private_key(65537, 2048)
pub = key.public_key()

os.makedirs(os.environ['APPDATA'] + '/AutoDoorProPublisher/keys', exist_ok=True)
with open(os.environ['APPDATA'] + '/AutoDoorProPublisher/keys/release_private.pem', 'wb') as f:
    f.write(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

with open('resources/security/release_public.pem', 'wb') as f:
    f.write(pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))

print('密钥已生成')
"
```

2. 私钥保存在 `%APPDATA%/AutoDoorProPublisher/keys/release_private.pem`
3. 公钥已提交到 `resources/security/release_public.pem`
4. 私钥永远不进 git

## 混淆器配置

在发布 UI 中设置混淆器路径，或通过 config.json：

```json
{
  "obfuscator_path": "C:/tools/ConfuserEx/Confuser.CLI.exe"
}
```

混淆器脚本位于 `tools/protect_csharp.ps1`，需编辑 TODO 位置接入实际命令。

## 使用发布 UI

```bash
python tools/release_publisher_ui.py
```

UI 功能：

1. 版本信息设置
2. 路径配置
3. 分步执行（检查环境 → 构建 → 混淆 → 生成 manifest → 签名 → 打包 → 检查 → 发布）
4. 一键发布
5. 实时日志

## 一键发布（CLI）

```bash
build_release.bat 1.6.1
```

或：

```bash
python tools/release_pipeline.py \
  --version 1.6.1 \
  --channel stable \
  --platform win-x64 \
  --mode release \
  --private-key "%APPDATA%/AutoDoorProPublisher/keys/release_private.pem"
```

## 发布产物

```
release/
  AutoDoorPro-v1.6.1/
    dist/                    # 商业包
    update/
      AutoDoorPro-v1.6.1-win-x64.zip    # 更新包
      manifest.json                      # 文件清单 + hash
      manifest.sig                       # 签名
      latest.json                        # 版本信息
```

## 上传到更新服务器

将 `release/AutoDoorPro-v1.6.1/update/` 目录上传到 HTTP/HTTPS 服务器。

用户端配置更新服务器 URL（通过 VersionChecker 或 UpdateService）。

## 回滚

update_agent 在替换文件前会备份当前版本到：

```
%APPDATA%/AutoDoorPro/backups/
```

更新失败自动回滚。

## 不提交 git 的文件

- `*.pem` / `*.key` / `*.pfx` / `*.p12`（私钥相关）
- `release/` 目录
- `dist/` 目录
- `%APPDATA%/AutoDoorProPublisher/config.json`
- 所有 `__pycache__` / `*.pyc` / `*.pyo`

## 授权系统

更新系统不会修改现有的授权/许可系统。更新后授权状态保持不变。

## 注意事项

- 每次发布前先提交当前代码
- release 模式必须配置混淆器
- 发布前运行 `check_update_system.py` 验证完整性
