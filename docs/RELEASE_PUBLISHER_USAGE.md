# AutoDoor Pro 加密发布中心使用说明

## 1. 发布中心位置

```text
tools/release_publisher_ui.py
```

启动方式：

```bash
python tools/release_publisher_ui.py
```

或双击：

```text
start_release_publisher.bat
```

## 2. 打开后先点：自动搜索路径

点击后会自动识别：

- 项目路径（自动设为根目录）
- dist 目录（按 dist/AutoDoorPro > dist > release/*/dist 顺序搜索）
- release 目录（项目根目录/release）
- 私钥路径（搜索 APPDATA > USERPROFILE > 项目目录）
- 混淆器路径（搜索 D:/Tools 和 C:/Tools 常见位置）
- 更新服务器 URL（根据版本号/通道/平台自动生成）

## 3. 测试演练点：填充测试配置

点击后自动填入：

- version = 1.6.1-test
- channel = internal
- platform = win-x64
- mode = dev
- base_update_url = https://example.com/updates/internal/win-x64/1.6.1-test

然后自动执行路径搜索。

## 4. 没有私钥点：生成测试私钥

私钥生成到：

```text
%APPDATA%\AutoDoorProPublisher\keys\release_private.pem
```

公钥生成到：

```text
resources/security/release_public.pem
```

私钥不会放到项目目录，禁止提交 git。

## 5. 正式发布必须配置：真实混淆器路径

release 模式必须配置真实混淆器路径，否则不允许执行。

dev 模式可以跳过混淆。

## 6. 任务卡住可点：停止任务

所有长任务都有超时保护：

| 任务 | 超时 |
|---|---|
| 检查环境 | 120s |
| 构建商业包 | 1800s |
| 加密/混淆 | 600s |
| 生成 Manifest | 120s |
| 签名 Manifest | 120s |
| 生成更新包 | 300s |
| 检查发布包 | 120s |
| 一键发布 | 2400s |

超时或手动点击"停止任务"会终止当前进程。

## 7. 发布流程

1. 打开发布中心
2. 点击"自动搜索路径"
3. 确认版本号、通道、平台
4. 选择模式（dev/release）
5. 如有需要点击"填充测试配置"（dev 演练）
6. 如无私钥点击"生成测试私钥"
7. release 模式确保混淆器路径正确
8. 填写更新服务器 URL
9. 点击"一键发布"

## 8. 私钥位置

推荐私钥位置：

```text
%APPDATA%\AutoDoorProPublisher\keys\release_private.pem
```

禁止放到项目目录，禁止提交 git。

## 9. 公钥位置

```text
resources/security/release_public.pem
```

公钥可以提交。

## 10. 常见问题

### 1. 测试 URL 不能写成 1.6.1-test-test

填充测试配置后应为：

```text
https://example.com/updates/internal/win-x64/1.6.1-test
```

### 2. 服务器发布目录不会传给 release_pipeline

服务器发布目录只是给人工上传/复制使用，不传给 release_pipeline.py。

### 3. 单步加密/混淆按钮

单步加密/混淆会直接调用：

```text
tools/protect_csharp.ps1
```

## Obfuscar 免费混淆器

发布中心支持免费 Obfuscar。

按钮：

```text
安装 Obfuscar
```

安装后点击：

```text
自动搜索路径
```

会自动填入混淆器路径。

release 模式必须真实执行 Obfuscar，不能只复制文件。

## 生产发布注意

发布中心 release 模式必须确认：

```text
1. Obfuscar 已识别
2. release 模式不是 dev fallback
3. update zip 来自 protected_dist_dir
4. CoreService 目录包含 appsettings.json / runtimeconfig / deps.json
```
