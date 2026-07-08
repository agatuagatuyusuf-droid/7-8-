# CoreService IPC 协议

## 概述

Python UI 与 C# CoreService 通过 TCP 进行 JSON 消息通信。

## 传输层

- 协议: TCP
- Host: 127.0.0.1
- Port: 19527（可通过环境变量 AUTODOOR_CORE_HOST/AUTODOOR_CORE_PORT 覆盖）
- 编码: UTF-8 JSON（无 BOM）
- 消息分隔: 每条消息以 `\n` 换行分隔
- 通信模式: 请求/响应

## 消息格式

### 请求

```json
{
  "id": "uuid",
  "type": "request",
  "action": "license.status",
  "payload": {}
}
```

### 响应

```json
{
  "id": "uuid",
  "type": "response",
  "success": true,
  "error_code": null,
  "message": "",
  "data": {}
}
```

## 错误码

| 错误码 | 说明 |
|--------|------|
| NOT_CONNECTED | 未连接到 CoreService |
| IPC_DISCONNECTED | 连接断开 |
| IPC_TIMEOUT | 请求超时 |
| IPC_INVALID_JSON | JSON 解析失败 |
| IPC_SEND_FAILED | 发送失败 |
| IPC_RECV_FAILED | 接收失败 |
| CORE_CONNECT_FAILED | 连接失败 |
| UNKNOWN_ACTION | 未知 action |
| UNKNOWN_TYPE | 未知消息类型 |
| MISSING_CODE | 缺少激活码 |
| MISSING_FEATURE | 缺少功能名称 |
| MISSING_TREE | 缺少行为树数据 |
| NETWORK_ERROR | 网络错误 |
| INVALID_TICKET | 授权票据无效 |
| ACTIVATE_FAILED | 激活失败 |
| RUNTIME_NOT_IMPLEMENTED | 运行时功能未实现 |
| NODE_NOT_IMPLEMENTED | 节点类型未实现 |
| TREE_PARSE_ERROR | 行为树解析错误 |

## Action 列表

### 系统

| Action | 说明 |
|--------|------|
| core.hello | 心跳检测，返回 `{"status": "running"}` |
| core.shutdown | 关闭 CoreService |

### 授权

| Action | 说明 | 请求 Payload |
|--------|------|-------------|
| license.machine_code | 获取机器码 | 无 |
| license.activate | 激活授权 | `{ "code": "xxx" }` |
| license.status | 获取授权状态 | 无 |
| license.refresh | 刷新授权 | 无 |
| license.deactivate | 解除授权 | 无 |

### license.status 响应

```json
{
  "success": true,
  "data": {
    "activated": true,
    "valid": true,
    "expired": false,
    "machine_match": true,
    "expire_at": "2028-07-08T00:00:00Z",
    "edition": "pro",
    "license_id": "LIC-001",
    "features": ["basic_editor", "basic_input", "schedule", "ocr", "image_match"],
    "error": null
  }
}
```

- `activated`: 是否有本地缓存的票据
- `valid`: 是否有效（activated + 签名有效 + 未过期 + 机器匹配）
- `expired`: 是否过期
- `machine_match`: 当前机器是否匹配

### 功能权限

| Action | 说明 | 请求 Payload |
|--------|------|-------------|
| feature.check | 检查功能权限 | `{ "feature": "ocr" }` |
| feature.list | 获取功能列表 | 无 |

### 行为树运行时

| Action | 说明 | 请求 Payload |
|--------|------|-------------|
| tree.validate | 验证行为树 | `{ "tree": { ... } }` |
| tree.start | 启动运行 | `{ "tree": { ... } }` |
| tree.pause | 暂停运行 | 无 |
| tree.resume | 恢复运行 | 无 |
| tree.stop | 停止运行 | 无 |
| tree.status | 获取运行状态 | 无 |

### tree.status 响应

```json
{
  "running": false,
  "paused": false,
  "completed": true,
  "status": "success",
  "tick_count": 123,
  "elapsed_ms": 1000,
  "last_error": null
}
```

### 运行时信息

| Action | 说明 |
|--------|------|
| runtime.logs | 获取运行日志 |
| runtime.stats | 获取运行统计 |
