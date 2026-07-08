# CoreService IPC 协议

## 概述

Python UI 与 C# CoreService 通过 Named Pipe 进行 JSON 消息通信。

## 传输层

- 协议: Named Pipe (Windows)
- Pipe 名称: `\\.\pipe\AutoDoorPro.CoreService`
- 编码: UTF-8 JSON
- 消息分隔: 每条消息以 `\n` 换行分隔

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

### 事件

```json
{
  "type": "event",
  "event": "runtime.node_status",
  "data": {
    "node_id": "abc123",
    "status": "success"
  }
}
```

## Action 列表

### 系统

| Action | 说明 |
|--------|------|
| core.hello | 心跳检测 |
| core.shutdown | 关闭 CoreService |

### 授权

| Action | 说明 |
|--------|------|
| license.machine_code | 获取机器码 |
| license.activate | 激活授权 |
| license.status | 获取授权状态 |
| license.refresh | 刷新授权 |
| license.deactivate | 解除授权 |

### 功能权限

| Action | 说明 |
|--------|------|
| feature.check | 检查功能权限 |
| feature.list | 获取功能列表 |

### 行为树运行时

| Action | 说明 |
|--------|------|
| tree.validate | 验证行为树 |
| tree.start | 启动运行 |
| tree.pause | 暂停运行 |
| tree.resume | 恢复运行 |
| tree.stop | 停止运行 |
| tree.status | 获取运行状态 |

### 运行时信息

| Action | 说明 |
|--------|------|
| runtime.logs | 获取运行日志 |
| runtime.stats | 获取运行统计 |
