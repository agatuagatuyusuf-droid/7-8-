# AutoDoor Pro 免费 C# 混淆器 Obfuscar 接入说明

## 1. 目标

使用免费 Obfuscar 对 C# CoreService 做基础混淆。

## 2. 安装

```powershell
powershell -ExecutionPolicy Bypass -File tools/install_obfuscar.ps1
```

默认安装到：

```text
tools/.dotnet-tools/
```

该目录不会提交 git。

## 3. 查找

```powershell
powershell -ExecutionPolicy Bypass -File tools/find_obfuscar.ps1
```

## 4. 发布中心

打开：

```bash
python tools/release_publisher_ui.py
```

点击：

```text
安装 Obfuscar
自动搜索路径
加密/混淆
```

## 5. dev / release 区别

dev 模式：

```text
允许找不到 Obfuscar 时复制 fallback。
这不是混淆。
```

release 模式：

```text
必须找到 Obfuscar。
必须执行真实 Obfuscar。
不允许复制 fallback。
```

## 6. 注意

Obfuscar 是免费基础混淆，不是绝对防破解。
真正的保护还要靠：

* 核心逻辑迁移到 C#
* 登录 session
* 授权服务器
* 在线更新签名
* 行为风控

## 7. 生产版打包要求

正式 release 流程必须满足：

```text
原始 dist
  ↓
复制到 release/AutoDoorPro-版本/dist
  ↓
混淆 release/AutoDoorPro-版本/dist/CoreService
  ↓
用 release/AutoDoorPro-版本/dist 生成 update zip
```

禁止用原始 dist 直接生成 update zip。

否则会把未混淆 CoreService 打进发布包。

## 8. DLL 混淆目标

正式发布必须混淆：

```text
CoreService/AutoDoor.CoreService.dll
```

不能优先混淆：

```text
CoreService/AutoDoor.CoreService.exe
```

原因：

.NET 8 Windows 发布目录中的 exe 可能只是 apphost，真正业务 IL 在 dll 中。

release 模式必须验证：

```text
混淆前 AutoDoor.CoreService.dll hash
!=
混淆后 AutoDoor.CoreService.dll hash
```

如果 hash 一样，发布必须失败。
