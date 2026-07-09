# AutoDoor Pro C# Core Runtime 核心执行切片

## 1. 本轮迁移范围

本轮只迁移最小核心执行切片：

- 键盘输入
- 鼠标点击
- 文本输入

不迁移全部 OCR / 图像识别 / 行为树节点。

## 2. 新增 C# IPC Action

```text
core.input.key_press
core.input.text_input
core.input.mouse_click
```

## 3. 安全要求

所有 action 必须带：

```text
login_session
```

没有 login_session 返回：

```text
LOGIN_REQUIRED
```

## 4. Python 调用方式

Python 只能通过：

```text
bt_bridge/core_client.py
```

调用：

```python
core_input_key_press(...)
core_input_text_input(...)
core_input_mouse_click(...)
```

## 5. 后续阶段

下一步再逐步迁移：

* OCR 节点
* 图像匹配节点
* 行为树核心执行调度
* 节点参数校验
* 商业授权 feature gate
