# 更新系统 — Update System

## 更新流程

### 服务器端发布版本
```
POST /api/admin/version-releases
```
参数：
- Version: 版本号 (如 "2.0.0")
- Changelog: 更新说明
- DownloadUrl: 下载链接
- ForceUpdate: 是否强制更新
- MinSupportedVersion: 最低支持版本

### 客户端版本检查
客户端通过 `/api/client/version/latest` 获取最新版本。

### 心跳中的更新检查
```
POST /api/client/heartbeat
```
响应中包含 `force_update`, `latest_version`, `download_url` 字段。

如果 `force_update=true` 或当前版本低于 `min_supported_version`，客户端必须更新才能继续使用。

## 文件 Hash Manifest

发行时在 dist 中包含 `hash_manifest.json`，用于验证文件完整性。
