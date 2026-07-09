# 故障排查 — Troubleshooting

## 1. 服务器无法启动

| 症状 | 可能原因 | 解决方法 |
|---|---|---|
| Production 启动失败 | 缺少 PostgreSQL 配置 | 设置 `AUTODOOR_DB_PROVIDER=PostgreSQL` 和 `AUTODOOR_DB_CONNECTION_STRING` |
| Production 启动失败 | 缺少私钥 | 设置 `AUTODOOR_SERVER_PRIVATE_KEY_PEM` 或 `AUTODOOR_SERVER_PRIVATE_KEY_PATH` |
| JWT 签名错误 | Secret 不足 32 字符 | 设置 `AUTODOOR_JWT_SECRET` 为 64 字符随机字符串 |
| PostgreSQL 连接失败 | 数据库地址或凭据错误 | 检查 `AUTODOOR_DB_CONNECTION_STRING` |

## 2. CoreService 无法启动

| 症状 | 可能原因 | 解决方法 |
|---|---|---|
| 端口占用 | 19527 端口被占用 | 修改 appsettings.json 中的 Ipc:Port |
| DLL 加载失败 | 缺少 VC++ 运行时 | 安装 Visual C++ Redistributable |
| OpenCvSharp 失败 | 缺少 OpenCV | 安装 OpenCvSharp4 运行时依赖 |

## 3. 授权问题

| 症状 | 可能原因 | 解决方法 |
|---|---|---|
| 激活码无效 | 激活码已使用或已禁用 | 检查后台激活码状态 |
| 机器已封禁 | 机器码被管理员封禁 | 后台解封 | 
| 授权已过期 | 授权到期 | 后台续费 |
| 签名无效 | 公钥不匹配 | 确保 CoreService 使用正确的公钥 |

## 4. OCR 不可用

| 症状 | 可能原因 | 解决方法 |
|---|---|---|
| OCR 返回错误 | 缺少 OCRWorker.exe | 确保商业包中包含 OCRWorker |
| OCR 返回空 | Tesseract 模型缺失 | 检查 OCRWorker 依赖 |

## 5. 商业打包

| 症状 | 可能原因 | 解决方法 |
|---|---|---|
| build_commercial.bat 失败 | 缺少依赖 | 确保安装了 Python, .NET 8, PyInstaller |
| 检查脚本失败 | dist 结构不对 | 查看 dist 目录结构是否符合预期 |
