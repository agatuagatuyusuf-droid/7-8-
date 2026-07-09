# AutoDoor Pro 加密发布中心使用说明

## 1. 加密发布中心在哪

发布中心 UI：

```text
tools/release_publisher_ui.py
```

启动命令：

```bash
python tools/release_publisher_ui.py
```

双击启动：

```text
start_release_publisher.bat
```

## 2. 真正执行加密/混淆的脚本

```text
tools/protect_csharp.ps1
```

## 3. 一键发布脚本

```text
build_release.bat
```

用法：

```bat
build_release.bat <version> <private_key_path> <obfuscator_path> <base_update_url>
```

示例：

```bat
build_release.bat 1.6.1 "%APPDATA%\AutoDoorProPublisher\keys\release_private.pem" "D:\Tools\Obfuscator\obfuscator.exe" "https://your-domain.com/updates/stable/win-x64/1.6.1"
```

## 4. 当前加密状态

当前已经有发布中心和加密/混淆入口。

但是：

* 真实 C# 混淆器还没接入
* release 模式没有真实混淆器会失败
* dev 模式可以跳过混淆做发布演练
* 不允许把复制文件说成已加密

## 5. 私钥位置

推荐私钥位置：

```text
%APPDATA%\AutoDoorProPublisher\keys\release_private.pem
```

禁止放到项目目录。

禁止提交 git。

## 6. 公钥位置

```text
resources/security/release_public.pem
```

公钥可以提交。

## 7. 发布流程

1. 打开发布中心
2. 填版本号
3. 填私钥路径
4. 填混淆器路径
5. 填更新服务器 URL
6. 点击一键发布
7. 生成 update zip
8. 生成 manifest.json
9. 生成 manifest.sig
10. 生成 latest.json
11. 上传到 HTTPS 更新目录

## 8. 下一步

正式发布前必须接入真实 C# 混淆器。
