# 窗口绑定与文本处理功能实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为 AutoDoor 行为树系统新增窗口绑定功能和文本处理功能，支持相对坐标操作和动态文本交互。

**Architecture:** 采用新增独立节点的方式实现，保持向后兼容。新增 WindowManager 工具类封装窗口操作，新增 5 个节点（窗口绑定、相对坐标点击、相对坐标移动、文本输入、文本提取）实现具体功能。

**Tech Stack:** Python 3.10+, ctypes (Windows API), RapidOCR, ONNX Runtime

---

## Task 1: 创建 WindowManager 工具类

**Files:**
- Create: `bt_utils/window_manager.py`

**Step 1: 创建 WindowManager 类框架**

```python
"""
窗口管理器工具类

提供窗口句柄管理、坐标转换等功能
"""
import ctypes
from ctypes import wintypes
from typing import Optional, Tuple


class WindowManager:
    """窗口管理器
    
    提供窗口句柄管理、坐标转换等功能
    """
    
    # Windows API 常量
    GW_OWNER = 4
    
    @staticmethod
    def get_window_from_point(x: int, y: int) -> Optional[int]:
        """通过屏幕坐标获取窗口句柄
        
        Args:
            x: 屏幕X坐标
            y: 屏幕Y坐标
        
        Returns:
            窗口句柄，如果失败返回 None
        """
        try:
            user32 = ctypes.windll.user32
            point = wintypes.POINT(x, y)
            hwnd = user32.WindowFromPoint(point)
            return hwnd if hwnd else None
        except Exception:
            return None
    
    @staticmethod
    def get_window_rect(hwnd: int) -> Optional[Tuple[int, int, int, int]]:
        """获取窗口客户区矩形（相对于屏幕）
        
        Args:
            hwnd: 窗口句柄
        
        Returns:
            (left, top, right, bottom) 矩形，如果失败返回 None
        """
        try:
            user32 = ctypes.windll.user32
            rect = wintypes.RECT()
            
            # 获取客户区矩形
            if user32.GetClientRect(hwnd, ctypes.byref(rect)):
                # 转换为屏幕坐标
                point = wintypes.POINT(rect.left, rect.top)
                user32.ClientToScreen(hwnd, ctypes.byref(point))
                
                left = point.x
                top = point.y
                right = left + (rect.right - rect.left)
                bottom = top + (rect.bottom - rect.top)
                
                return (left, top, right, bottom)
            return None
        except Exception:
            return None
    
    @staticmethod
    def screen_to_client(hwnd: int, x: int, y: int) -> Tuple[int, int]:
        """屏幕坐标转窗口客户区坐标
        
        Args:
            hwnd: 窗口句柄
            x: 屏幕X坐标
            y: 屏幕Y坐标
        
        Returns:
            (client_x, client_y) 窗口客户区坐标
        """
        try:
            user32 = ctypes.windll.user32
            point = wintypes.POINT(x, y)
            user32.ScreenToClient(hwnd, ctypes.byref(point))
            return (point.x, point.y)
        except Exception:
            return (0, 0)
    
    @staticmethod
    def client_to_screen(hwnd: int, x: int, y: int) -> Tuple[int, int]:
        """窗口客户区坐标转屏幕坐标
        
        Args:
            hwnd: 窗口句柄
            x: 窗口客户区X坐标
            y: 窗口客户区Y坐标
        
        Returns:
            (screen_x, screen_y) 屏幕坐标
        """
        try:
            user32 = ctypes.windll.user32
            point = wintypes.POINT(x, y)
            user32.ClientToScreen(hwnd, ctypes.byref(point))
            return (point.x, point.y)
        except Exception:
            return (0, 0)
    
    @staticmethod
    def get_window_title(hwnd: int) -> str:
        """获取窗口标题
        
        Args:
            hwnd: 窗口句柄
        
        Returns:
            窗口标题
        """
        try:
            user32 = ctypes.windll.user32
            length = user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return ""
            
            buffer = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buffer, length + 1)
            return buffer.value
        except Exception:
            return ""
    
    @staticmethod
    def is_window_valid(hwnd: int) -> bool:
        """检查窗口是否有效
        
        Args:
            hwnd: 窗口句柄
        
        Returns:
            窗口是否有效
        """
        try:
            user32 = ctypes.windll.user32
            return bool(user32.IsWindow(hwnd))
        except Exception:
            return False
    
    @staticmethod
    def find_window_by_title(title: str) -> Optional[int]:
        """通过窗口标题查找窗口
        
        Args:
            title: 窗口标题（部分匹配）
        
        Returns:
            窗口句柄，如果未找到返回 None
        """
        try:
            user32 = ctypes.windll.user32
            
            def enum_windows_callback(hwnd, lParam):
                window_title = WindowManager.get_window_title(hwnd)
                if title.lower() in window_title.lower():
                    return hwnd
                return None
            
            # 枚举所有窗口
            result = [None]
            
            def callback(hwnd, lParam):
                window_title = WindowManager.get_window_title(hwnd)
                if title.lower() in window_title.lower():
                    result[0] = hwnd
                    return False
                return True
            
            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
            user32.EnumWindows(WNDENUMPROC(callback), 0)
            
            return result[0]
        except Exception:
            return None
```

**Step 2: 提交 WindowManager 工具类**

```bash
git add bt_utils/window_manager.py
git commit -m "feat: add WindowManager utility class for window operations"
```

---

## Task 2: 创建窗口绑定节点

**Files:**
- Create: `bt_nodes/actions/window_bind.py`

**Step 1: 创建 WindowBindNode 类**

```python
from bt_core.nodes import ActionNode, NodeStatus
from bt_core.config import NodeConfig
from typing import Dict, Any, Optional
from bt_utils.log_manager import LogManager
from bt_utils.window_manager import WindowManager


class WindowBindNode(ActionNode):
    """窗口绑定节点
    
    绑定目标窗口，将窗口句柄保存到黑板
    """
    NODE_TYPE = "WindowBindNode"
    
    def __init__(self, node_id: str = None, config: NodeConfig = None):
        super().__init__(node_id, config)
        self.window_key = self.config.get("window_key", "bound_window")
        self.window_title = self.config.get("window_title", "")
        self._hwnd = None
    
    def _execute_action(self, context) -> NodeStatus:
        try:
            # 如果提供了窗口标题，自动查找
            if self.window_title:
                hwnd = WindowManager.find_window_by_title(self.window_title)
                if hwnd is None:
                    LogManager.instance().log_failure(
                        node_type="窗口绑定节点",
                        node_name=self.name,
                        reason=f"未找到标题包含 '{self.window_title}' 的窗口"
                    )
                    return NodeStatus.FAILURE
            else:
                # 等待用户点击选择窗口
                hwnd = self._wait_for_window_selection(context)
                if hwnd is None:
                    LogManager.instance().log_failure(
                        node_type="窗口绑定节点",
                        node_name=self.name,
                        reason="窗口选择超时或取消"
                    )
                    return NodeStatus.FAILURE
            
            # 验证窗口有效性
            if not WindowManager.is_window_valid(hwnd):
                LogManager.instance().log_failure(
                    node_type="窗口绑定节点",
                    node_name=self.name,
                    reason="窗口句柄无效"
                )
                return NodeStatus.FAILURE
            
            # 保存窗口句柄到黑板
            context.blackboard.set(self.window_key, hwnd)
            self._hwnd = hwnd
            
            # 记录日志
            window_title = WindowManager.get_window_title(hwnd)
            LogManager.instance().log_success(
                node_type="窗口绑定节点",
                node_name=self.name
            )
            LogManager.instance().log_info(
                node_type="窗口绑定节点",
                node_name=self.name,
                message=f"已绑定窗口: {window_title} (句柄: {hwnd})"
            )
            
            return NodeStatus.SUCCESS
            
        except Exception as e:
            from bt_utils.exception_handler import log_exception
            log_exception(e, f"WindowBindNode '{self.name}'")
            LogManager.instance().log_failure(
                node_type="窗口绑定节点",
                node_name=self.name,
                reason="执行异常，详情见终端日志"
            )
            return NodeStatus.FAILURE
    
    def _wait_for_window_selection(self, context, timeout_ms: int = 30000) -> Optional[int]:
        """等待用户点击选择窗口
        
        Args:
            context: 执行上下文
            timeout_ms: 超时时间（毫秒）
        
        Returns:
            窗口句柄，如果超时或取消返回 None
        """
        import time
        import tkinter as tk
        from tkinter import messagebox
        
        # 显示提示
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(
            "窗口选择",
            "请点击要绑定的窗口\n\n点击确定后，鼠标将变成十字形状，\n然后点击目标窗口即可完成绑定。"
        )
        root.destroy()
        
        # 等待用户点击
        start_time = time.time() * 1000
        while True:
            if not context.check_running():
                return None
            
            current_time = time.time() * 1000
            if current_time - start_time > timeout_ms:
                return None
            
            # 检查鼠标点击
            import ctypes
            user32 = ctypes.windll.user32
            
            # VK_LBUTTON = 0x01
            if user32.GetAsyncKeyState(0x01) & 0x8000:
                # 获取鼠标位置
                point = wintypes.POINT()
                user32.GetCursorPos(ctypes.byref(point))
                
                # 获取窗口句柄
                hwnd = WindowManager.get_window_from_point(point.x, point.y)
                if hwnd:
                    time.sleep(0.1)  # 等待鼠标释放
                    return hwnd
            
            time.sleep(0.05)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["config"]["window_key"] = self.window_key
        data["config"]["window_title"] = self.window_title
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WindowBindNode":
        config = NodeConfig.from_dict(data.get("config", {}))
        node = cls(node_id=data.get("id"), config=config)
        return node
```

**Step 2: 提交窗口绑定节点**

```bash
git add bt_nodes/actions/window_bind.py
git commit -m "feat: add WindowBindNode for window binding"
```

---

## Task 3: 创建相对坐标点击节点

**Files:**
- Create: `bt_nodes/actions/relative_mouse.py`

**Step 1: 创建 RelativeMouseClickNode 类**

```python
from bt_core.nodes import ActionNode, NodeStatus
from bt_core.config import NodeConfig
from typing import Dict, Any, Tuple, Optional
from bt_utils.log_manager import LogManager
from bt_utils.window_manager import WindowManager
import time


class RelativeMouseClickNode(ActionNode):
    """相对坐标点击节点
    
    在绑定窗口的客户区内执行鼠标点击
    """
    NODE_TYPE = "RelativeMouseClickNode"
    
    def __init__(self, node_id: str = None, config: NodeConfig = None):
        super().__init__(node_id, config)
        self.window_key = self.config.get("window_key", "bound_window")
        self.position: Optional[Tuple[int, int]] = self.config.get("position", None)
        self.use_blackboard = self.config.get_bool("use_blackboard", False)
        self.position_key = self.config.get("position_key", "last_detection_position")
        self.button = self.config.get("button", "left")
        self.action = self.config.get("action", "press")
        self.duration = self.config.get_int("duration", 100)
        self.click_count = self.config.get_int("click_count", 1)
        self.click_interval = self.config.get_int("click_interval", 100)
    
    def _execute_action(self, context) -> NodeStatus:
        try:
            # 从黑板获取窗口句柄
            hwnd = context.blackboard.get(self.window_key)
            if hwnd is None:
                LogManager.instance().log_failure(
                    node_type="相对坐标点击节点",
                    node_name=self.name,
                    reason=f"未找到窗口句柄 '{self.window_key}'，请先使用窗口绑定节点"
                )
                return NodeStatus.FAILURE
            
            # 验证窗口有效性
            if not WindowManager.is_window_valid(hwnd):
                LogManager.instance().log_failure(
                    node_type="相对坐标点击节点",
                    node_name=self.name,
                    reason="窗口句柄无效，窗口可能已关闭"
                )
                return NodeStatus.FAILURE
            
            # 获取点击位置
            position = self._get_position(context)
            if position is None:
                LogManager.instance().log_failure(
                    node_type="相对坐标点击节点",
                    node_name=self.name,
                    reason="未指定点击位置"
                )
                return NodeStatus.FAILURE
            
            # 转换为屏幕坐标
            screen_pos = WindowManager.client_to_screen(hwnd, position[0], position[1])
            
            # 执行点击
            context.execute_mouse_click(
                self.button, screen_pos, self.action, self.duration
            )
            
            LogManager.instance().log_success(
                node_type="相对坐标点击节点",
                node_name=self.name
            )
            
            return NodeStatus.SUCCESS
            
        except Exception as e:
            from bt_utils.exception_handler import log_exception
            log_exception(e, f"RelativeMouseClickNode '{self.name}'")
            LogManager.instance().log_failure(
                node_type="相对坐标点击节点",
                node_name=self.name,
                reason="执行异常，详情见终端日志"
            )
            return NodeStatus.FAILURE
    
    def _get_position(self, context) -> Optional[Tuple[int, int]]:
        """获取点击位置"""
        if self.use_blackboard:
            return context.blackboard.get(self.position_key)
        return self.position
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["config"]["window_key"] = self.window_key
        data["config"]["position"] = self.position
        data["config"]["use_blackboard"] = self.use_blackboard
        data["config"]["position_key"] = self.position_key
        data["config"]["button"] = self.button
        data["config"]["action"] = self.action
        data["config"]["duration"] = self.duration
        data["config"]["click_count"] = self.click_count
        data["config"]["click_interval"] = self.click_interval
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RelativeMouseClickNode":
        config = NodeConfig.from_dict(data.get("config", {}))
        node = cls(node_id=data.get("id"), config=config)
        return node
```

**Step 2: 提交相对坐标点击节点**

```bash
git add bt_nodes/actions/relative_mouse.py
git commit -m "feat: add RelativeMouseClickNode for relative coordinate clicking"
```

---

## Task 4: 创建相对坐标移动节点

**Files:**
- Modify: `bt_nodes/actions/relative_mouse.py`

**Step 1: 在 relative_mouse.py 中添加 RelativeMouseMoveNode 类**

```python
class RelativeMouseMoveNode(ActionNode):
    """相对坐标移动节点
    
    在绑定窗口的客户区内移动鼠标
    """
    NODE_TYPE = "RelativeMouseMoveNode"
    
    def __init__(self, node_id: str = None, config: NodeConfig = None):
        super().__init__(node_id, config)
        self.window_key = self.config.get("window_key", "bound_window")
        self.position: Optional[Tuple[int, int]] = self.config.get("position", None)
        self.use_blackboard = self.config.get_bool("use_blackboard", False)
        self.position_key = self.config.get("position_key", "last_detection_position")
        self.smooth = self.config.get_bool("smooth", False)
        self.duration = self.config.get_int("duration", 300)
    
    def _execute_action(self, context) -> NodeStatus:
        try:
            # 从黑板获取窗口句柄
            hwnd = context.blackboard.get(self.window_key)
            if hwnd is None:
                LogManager.instance().log_failure(
                    node_type="相对坐标移动节点",
                    node_name=self.name,
                    reason=f"未找到窗口句柄 '{self.window_key}'，请先使用窗口绑定节点"
                )
                return NodeStatus.FAILURE
            
            # 验证窗口有效性
            if not WindowManager.is_window_valid(hwnd):
                LogManager.instance().log_failure(
                    node_type="相对坐标移动节点",
                    node_name=self.name,
                    reason="窗口句柄无效，窗口可能已关闭"
                )
                return NodeStatus.FAILURE
            
            # 获取目标位置
            position = self._get_position(context)
            if position is None:
                LogManager.instance().log_failure(
                    node_type="相对坐标移动节点",
                    node_name=self.name,
                    reason="未指定目标位置"
                )
                return NodeStatus.FAILURE
            
            # 转换为屏幕坐标
            screen_pos = WindowManager.client_to_screen(hwnd, position[0], position[1])
            
            # 执行移动
            context.execute_mouse_move(screen_pos, smooth=self.smooth)
            
            LogManager.instance().log_success(
                node_type="相对坐标移动节点",
                node_name=self.name
            )
            
            return NodeStatus.SUCCESS
            
        except Exception as e:
            from bt_utils.exception_handler import log_exception
            log_exception(e, f"RelativeMouseMoveNode '{self.name}'")
            LogManager.instance().log_failure(
                node_type="相对坐标移动节点",
                node_name=self.name,
                reason="执行异常，详情见终端日志"
            )
            return NodeStatus.FAILURE
    
    def _get_position(self, context) -> Optional[Tuple[int, int]]:
        """获取目标位置"""
        if self.use_blackboard:
            return context.blackboard.get(self.position_key)
        return self.position
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["config"]["window_key"] = self.window_key
        data["config"]["position"] = self.position
        data["config"]["use_blackboard"] = self.use_blackboard
        data["config"]["position_key"] = self.position_key
        data["config"]["smooth"] = self.smooth
        data["config"]["duration"] = self.duration
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RelativeMouseMoveNode":
        config = NodeConfig.from_dict(data.get("config", {}))
        node = cls(node_id=data.get("id"), config=config)
        return node
```

**Step 2: 提交相对坐标移动节点**

```bash
git add bt_nodes/actions/relative_mouse.py
git commit -m "feat: add RelativeMouseMoveNode for relative coordinate movement"
```

---

## Task 5: 创建文本输入节点

**Files:**
- Create: `bt_nodes/actions/text_input.py`

**Step 1: 创建 TextInputNode 类**

```python
from bt_core.nodes import ActionNode, NodeStatus
from bt_core.config import NodeConfig
from typing import Dict, Any, Tuple, Optional, List
from bt_utils.log_manager import LogManager
import os
import random
import time


class TextInputNode(ActionNode):
    """文本输入节点
    
    向目标位置输入文本，支持多种输入源和执行模式
    """
    NODE_TYPE = "TextInputNode"
    
    def __init__(self, node_id: str = None, config: NodeConfig = None):
        super().__init__(node_id, config)
        self.input_mode = self.config.get("input_mode", "preset")
        self.preset_texts: List[str] = self.config.get("preset_texts", [])
        self.execution_mode = self.config.get("execution_mode", "sequential")
        self.blackboard_key = self.config.get("blackboard_key", "extracted_text")
        self.file_path = self.config.get("file_path", "")
        self.position: Optional[Tuple[int, int]] = self.config.get("position", None)
        self.use_blackboard = self.config.get_bool("use_blackboard", False)
        self.position_key = self.config.get("position_key", "last_detection_position")
        self.input_delay = self.config.get_int("input_delay", 50)
        self.clear_before_input = self.config.get_bool("clear_before_input", False)
        self.save_input_text = self.config.get_bool("save_input_text", False)
        self.output_key = self.config.get("output_key", "last_input_text")
        self._current_text_index = 0
    
    def _execute_action(self, context) -> NodeStatus:
        try:
            # 获取文本内容
            text = self._get_text(context)
            if not text:
                LogManager.instance().log_failure(
                    node_type="文本输入节点",
                    node_name=self.name,
                    reason="未获取到文本内容"
                )
                return NodeStatus.FAILURE
            
            # 获取输入位置（可选）
            if self.use_blackboard:
                position = context.blackboard.get(self.position_key)
            else:
                position = self.position
            
            # 移动鼠标到目标位置（如果指定了位置）
            if position:
                context.execute_mouse_move(position)
                time.sleep(0.1)
            
            # 清空现有内容（可选）
            if self.clear_before_input:
                context.execute_key_press("ctrl", action="down")
                context.execute_key_press("a", action="press")
                context.execute_key_press("ctrl", action="up")
                time.sleep(0.1)
            
            # 逐字符输入文本
            self._input_text(context, text)
            
            # 保存输入的文本（可选）
            if self.save_input_text:
                context.blackboard.set(self.output_key, text)
            
            LogManager.instance().log_success(
                node_type="文本输入节点",
                node_name=self.name
            )
            
            return NodeStatus.SUCCESS
            
        except Exception as e:
            from bt_utils.exception_handler import log_exception
            log_exception(e, f"TextInputNode '{self.name}'")
            LogManager.instance().log_failure(
                node_type="文本输入节点",
                node_name=self.name,
                reason="执行异常，详情见终端日志"
            )
            return NodeStatus.FAILURE
    
    def _get_text(self, context) -> str:
        """根据输入模式获取文本内容"""
        if self.input_mode == "preset":
            if not self.preset_texts:
                return ""
            
            if self.execution_mode == "sequential":
                return self._get_next_preset_text(context)
            else:  # random
                return self._get_random_preset_text()
        
        elif self.input_mode == "blackboard":
            return context.blackboard.get(self.blackboard_key, "")
        
        elif self.input_mode == "file":
            return self._read_file(context)
        
        return ""
    
    def _get_next_preset_text(self, context) -> str:
        """获取下一个预设文本（顺序执行）"""
        # 从黑板读取当前索引
        index_key = f"{self.node_id}_text_index"
        current_index = context.blackboard.get(index_key, 0)
        
        # 获取文本
        text = self.preset_texts[current_index % len(self.preset_texts)]
        
        # 更新索引
        next_index = (current_index + 1) % len(self.preset_texts)
        context.blackboard.set(index_key, next_index)
        
        return text
    
    def _get_random_preset_text(self) -> str:
        """随机获取预设文本"""
        return random.choice(self.preset_texts)
    
    def _read_file(self, context) -> str:
        """读取文件内容"""
        try:
            # 解析文件路径
            if self.file_path.startswith("./"):
                file_path = context.resolve_path(self.file_path)
            else:
                file_path = self.file_path
            
            if not os.path.exists(file_path):
                LogManager.instance().log_failure(
                    node_type="文本输入节点",
                    node_name=self.name,
                    reason=f"文件不存在: {file_path}"
                )
                return ""
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        except Exception as e:
            LogManager.instance().log_failure(
                node_type="文本输入节点",
                node_name=self.name,
                reason=f"读取文件失败: {str(e)}"
            )
            return ""
    
    def _input_text(self, context, text: str) -> None:
        """逐字符输入文本"""
        for char in text:
            if not context.check_running():
                break
            
            # 输入字符
            if char == '\n':
                context.execute_key_press("enter", action="press")
            elif char == '\t':
                context.execute_key_press("tab", action="press")
            else:
                # 使用剪贴板输入（更可靠）
                import pyperclip
                pyperclip.copy(char)
                context.execute_key_press("ctrl", action="down")
                context.execute_key_press("v", action="press")
                context.execute_key_press("ctrl", action="up")
            
            # 延时
            if self.input_delay > 0:
                time.sleep(self.input_delay / 1000.0)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["config"]["input_mode"] = self.input_mode
        data["config"]["preset_texts"] = self.preset_texts
        data["config"]["execution_mode"] = self.execution_mode
        data["config"]["blackboard_key"] = self.blackboard_key
        data["config"]["file_path"] = self.file_path
        data["config"]["position"] = self.position
        data["config"]["use_blackboard"] = self.use_blackboard
        data["config"]["position_key"] = self.position_key
        data["config"]["input_delay"] = self.input_delay
        data["config"]["clear_before_input"] = self.clear_before_input
        data["config"]["save_input_text"] = self.save_input_text
        data["config"]["output_key"] = self.output_key
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TextInputNode":
        config = NodeConfig.from_dict(data.get("config", {}))
        node = cls(node_id=data.get("id"), config=config)
        return node
```

**Step 2: 提交文本输入节点**

```bash
git add bt_nodes/actions/text_input.py
git commit -m "feat: add TextInputNode for text input with multiple input modes"
```

---

## Task 6: 创建文本提取节点

**Files:**
- Create: `bt_nodes/conditions/text_extract.py`

**Step 1: 创建 TextExtractNode 类**

```python
from bt_core.nodes import ConditionNode
from bt_core.config import NodeConfig
from typing import Dict, Any, Tuple, Optional
from bt_utils.log_manager import LogManager
from bt_utils.ocr_manager import OCRManager


LANGUAGE_MAP = {
    "English": "eng",
    "简体中文": "chi_sim",
    "繁体中文": "chi_tra",
    "eng": "eng",
    "chi_sim": "chi_sim",
    "chi_tra": "chi_tra",
}


class TextExtractNode(ConditionNode):
    """文本提取节点
    
    从指定区域提取文本并保存到黑板
    """
    NODE_TYPE = "TextExtractNode"
    
    def __init__(self, node_id: str = None, config: NodeConfig = None):
        super().__init__(node_id, config)
        self.extract_mode = self.config.get("extract_mode", "all")
        self.region: Optional[Tuple[int, int, int, int]] = self._parse_region(
            self.config.get("region", None)
        )
        self.keywords = self.config.get("keywords", "")
        language_display = self.config.get("language", "简体中文")
        self.language = LANGUAGE_MAP.get(language_display, "chi_sim")
        preprocess_display = self.config.get("preprocess_mode", "默认")
        self.preprocess_mode = "game" if preprocess_display == "复杂色彩" else "normal"
        self.output_key = self.config.get("output_key", "extracted_text")
        self.save_all_text = self.config.get_bool("save_all_text", False)
        self.all_text_key = self.config.get("all_text_key", "all_ocr_text")
        self.save_position = self.config.get_bool("save_position", True)
        self.position_key = self.config.get("position_key", "last_detection_position")
    
    def _check_condition(self, context) -> bool:
        try:
            # 获取截图
            screenshot = self._get_region_image(context)
            if screenshot is None:
                return False
            
            # 执行OCR识别
            ocr_manager = OCRManager()
            all_text = ocr_manager.get_all_text(
                screenshot, self.language, self.preprocess_mode
            )
            
            if not all_text:
                self._log_condition_result(False, "未识别到文本")
                return False
            
            # 根据提取模式处理结果
            if self.extract_mode == "all":
                extracted_text = all_text
            else:  # keywords
                extracted_text = self._extract_keywords_text(all_text, self.keywords)
            
            # 保存提取的文本
            context.blackboard.set(self.output_key, extracted_text)
            
            # 可选：保存所有识别文本
            if self.save_all_text:
                context.blackboard.set(self.all_text_key, all_text)
            
            # 可选：保存检测位置
            if self.save_position and self.region:
                center_x = (self.region[0] + self.region[2]) // 2
                center_y = (self.region[1] + self.region[3]) // 2
                context.blackboard.set(self.position_key, (center_x, center_y))
            
            # 记录日志
            if extracted_text:
                self._log_condition_result(True)
                LogManager.instance().log_info(
                    node_type="文本提取节点",
                    node_name=self.name,
                    message=f"提取文本: {extracted_text[:50]}..."
                )
                return True
            else:
                self._log_condition_result(False, "未提取到匹配的文本")
                return False
            
        except Exception as e:
            from bt_utils.exception_handler import log_exception
            log_exception(e, f"TextExtractNode '{self.name}'")
            self._log_condition_result(False, "执行异常，详情见终端日志")
            return False
    
    def _extract_keywords_text(self, all_text: str, keywords: str) -> str:
        """提取包含关键词的文本行"""
        lines = all_text.split('\n')
        matched_lines = []
        
        for line in lines:
            line = line.strip()
            if line and keywords in line:
                matched_lines.append(line)
        
        return '\n'.join(matched_lines)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["config"]["extract_mode"] = self.extract_mode
        data["config"]["region"] = list(self.region) if self.region else None
        data["config"]["keywords"] = self.keywords
        reverse_language_map = {"eng": "English", "chi_sim": "简体中文", "chi_tra": "繁体中文"}
        data["config"]["language"] = reverse_language_map.get(self.language, self.language)
        data["config"]["preprocess_mode"] = "复杂色彩" if self.preprocess_mode == "game" else "默认"
        data["config"]["output_key"] = self.output_key
        data["config"]["save_all_text"] = self.save_all_text
        data["config"]["all_text_key"] = self.all_text_key
        data["config"]["save_position"] = self.save_position
        data["config"]["position_key"] = self.position_key
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TextExtractNode":
        config = NodeConfig.from_dict(data.get("config", {}))
        node = cls(node_id=data.get("id"), config=config)
        return node
```

**Step 2: 提交文本提取节点**

```bash
git add bt_nodes/conditions/text_extract.py
git commit -m "feat: add TextExtractNode for text extraction with OCR"
```

---

## Task 7: 注册新节点到节点注册中心

**Files:**
- Modify: `bt_core/registry.py`

**Step 1: 在 registry.py 中导入并注册新节点**

```python
# 在文件顶部添加导入
from bt_nodes.actions.window_bind import WindowBindNode
from bt_nodes.actions.relative_mouse import RelativeMouseClickNode, RelativeMouseMoveNode
from bt_nodes.actions.text_input import TextInputNode
from bt_nodes.conditions.text_extract import TextExtractNode

# 在注册部分添加
NodeRegistry.register("WindowBindNode", WindowBindNode)
NodeRegistry.register("RelativeMouseClickNode", RelativeMouseClickNode)
NodeRegistry.register("RelativeMouseMoveNode", RelativeMouseMoveNode)
NodeRegistry.register("TextInputNode", TextInputNode)
NodeRegistry.register("TextExtractNode", TextExtractNode)
```

**Step 2: 提交节点注册**

```bash
git add bt_core/registry.py
git commit -m "feat: register new nodes to NodeRegistry"
```

---

## Task 8: 更新节点面板配置

**Files:**
- Modify: `bt_gui/bt_editor/constants.py`

**Step 1: 在 constants.py 中添加新节点类型**

```python
# 在 NODE_TYPES 字典中添加
NODE_TYPES = {
    # ... 现有节点 ...
    
    # 窗口相关节点
    "WindowBindNode": {
        "name": "窗口绑定",
        "category": "action",
        "color": "#9C27B0",
        "description": "绑定目标窗口，将窗口句柄保存到黑板"
    },
    "RelativeMouseClickNode": {
        "name": "相对坐标点击",
        "category": "action",
        "color": "#9C27B0",
        "description": "在绑定窗口的客户区内执行鼠标点击"
    },
    "RelativeMouseMoveNode": {
        "name": "相对坐标移动",
        "category": "action",
        "color": "#9C27B0",
        "description": "在绑定窗口的客户区内移动鼠标"
    },
    
    # 文本处理节点
    "TextInputNode": {
        "name": "文本输入",
        "category": "action",
        "color": "#FF5722",
        "description": "向目标位置输入文本"
    },
    "TextExtractNode": {
        "name": "文本提取",
        "category": "condition",
        "color": "#FF5722",
        "description": "从指定区域提取文本并保存到黑板"
    },
}
```

**Step 2: 提交节点面板配置**

```bash
git add bt_gui/bt_editor/constants.py
git commit -m "feat: add new node types to constants"
```

---

## Task 9: 更新属性面板支持新字段类型

**Files:**
- Modify: `bt_gui/bt_editor/property.py`

**Step 1: 添加窗口选择器字段**

```python
class WindowSelectorField:
    """窗口选择器字段"""
    
    def __init__(self, master, label: str, key: str, value: str = "", on_change=None):
        self.master = master
        self.label = label
        self.key = key
        self.on_change = on_change
        self._hwnd = None
        
        self._create_widget()
        self.set_value(value)
    
    def _create_widget(self):
        # 创建框架
        self.frame = customtkinter.CTkFrame(self.master)
        self.frame.pack(fill="x", padx=5, pady=2)
        
        # 标签
        label = customtkinter.CTkLabel(self.frame, text=self.label, width=80, anchor="w")
        label.pack(side="left", padx=5)
        
        # 输入框
        self.entry = customtkinter.CTkEntry(self.frame, width=150)
        self.entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # 选择按钮
        self.select_btn = customtkinter.CTkButton(
            self.frame, text="选择窗口", width=80,
            command=self._select_window
        )
        self.select_btn.pack(side="left", padx=5)
    
    def _select_window(self):
        """选择窗口"""
        import tkinter as tk
        from tkinter import messagebox
        from bt_utils.window_manager import WindowManager
        
        # 显示提示
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(
            "窗口选择",
            "请点击要绑定的窗口\n\n点击确定后，鼠标将变成十字形状，\n然后点击目标窗口即可完成绑定。"
        )
        root.destroy()
        
        # 等待用户点击
        import time
        import ctypes
        from ctypes import wintypes
        
        user32 = ctypes.windll.user32
        
        while True:
            # VK_LBUTTON = 0x01
            if user32.GetAsyncKeyState(0x01) & 0x8000:
                # 获取鼠标位置
                point = wintypes.POINT()
                user32.GetCursorPos(ctypes.byref(point))
                
                # 获取窗口句柄
                hwnd = WindowManager.get_window_from_point(point.x, point.y)
                if hwnd:
                    time.sleep(0.1)  # 等待鼠标释放
                    
                    # 获取窗口标题
                    title = WindowManager.get_window_title(hwnd)
                    
                    # 更新显示
                    self.entry.delete(0, tk.END)
                    self.entry.insert(0, title)
                    self._hwnd = hwnd
                    
                    # 触发回调
                    if self.on_change:
                        self.on_change(self.key, hwnd)
                    
                    break
            
            time.sleep(0.05)
    
    def get_value(self):
        return self._hwnd
    
    def set_value(self, value):
        if value:
            self._hwnd = value
            title = WindowManager.get_window_title(value)
            self.entry.delete(0, tk.END)
            self.entry.insert(0, title)
```

**Step 2: 添加文本列表字段**

```python
class TextListField:
    """文本列表字段"""
    
    def __init__(self, master, label: str, key: str, value: list = None, on_change=None):
        self.master = master
        self.label = label
        self.key = key
        self.on_change = on_change
        self._texts = value or []
        
        self._create_widget()
    
    def _create_widget(self):
        # 创建框架
        self.frame = customtkinter.CTkFrame(self.master)
        self.frame.pack(fill="x", padx=5, pady=2)
        
        # 标签
        label = customtkinter.CTkLabel(self.frame, text=self.label, width=80, anchor="w")
        label.pack(side="top", padx=5, pady=2)
        
        # 文本框
        self.textbox = customtkinter.CTkTextbox(self.frame, height=100)
        self.textbox.pack(fill="x", padx=5, pady=2)
        
        # 填充初始值
        self.set_value(self._texts)
    
    def get_value(self) -> list:
        """获取文本列表"""
        text = self.textbox.get("1.0", tk.END).strip()
        if not text:
            return []
        return [line.strip() for line in text.split('\n') if line.strip()]
    
    def set_value(self, value: list):
        """设置文本列表"""
        self.textbox.delete("1.0", tk.END)
        if value:
            self.textbox.insert("1.0", '\n'.join(value))
```

**Step 3: 提交属性面板更新**

```bash
git add bt_gui/bt_editor/property.py
git commit -m "feat: add window selector and text list fields to property panel"
```

---

## Task 10: 更新文档

**Files:**
- Modify: `doc/01_架构文档.md`
- Modify: `doc/02_详细实现方法.md`
- Modify: `doc/04_节点功能速查表.md`

**Step 1: 在架构文档中添加新节点说明**

在 `doc/01_架构文档.md` 的节点模型部分添加：

```markdown
**新增节点（窗口绑定与文本处理）：**

| 节点类型 | 说明 |
|----------|------|
| WindowBindNode | 窗口绑定节点，绑定目标窗口并保存句柄到黑板 |
| RelativeMouseClickNode | 相对坐标点击节点，在绑定窗口内执行点击 |
| RelativeMouseMoveNode | 相对坐标移动节点，在绑定窗口内移动鼠标 |
| TextInputNode | 文本输入节点，支持多种输入源和执行模式 |
| TextExtractNode | 文本提取节点，从区域提取文本并保存到黑板 |
```

**Step 2: 提交文档更新**

```bash
git add doc/01_架构文档.md doc/02_详细实现方法.md doc/04_节点功能速查表.md
git commit -m "docs: update documentation for new nodes"
```

---

## Task 11: 添加依赖项

**Files:**
- Modify: `requirements.txt`

**Step 1: 添加 pyperclip 依赖**

```
pyperclip>=1.8.2
```

**Step 2: 提交依赖更新**

```bash
git add requirements.txt
git commit -m "feat: add pyperclip dependency for text input"
```

---

## Task 12: 最终测试与提交

**Step 1: 运行测试**

```bash
python -m pytest tests/ -v
```

**Step 2: 检查代码风格**

```bash
python -m flake8 bt_utils/window_manager.py bt_nodes/actions/window_bind.py bt_nodes/actions/relative_mouse.py bt_nodes/actions/text_input.py bt_nodes/conditions/text_extract.py
```

**Step 3: 最终提交**

```bash
git add .
git commit -m "feat: complete window binding and text processing features"
```

---

## 执行选择

**计划已完成并保存到 `docs/plans/2026-04-23-window-bind-and-text-processing-tasks.md`。两种执行方式：**

**1. Subagent-Driven (当前会话)** - 我在当前会话中逐个任务分派子代理执行，任务间进行代码审查，快速迭代

**2. Parallel Session (独立会话)** - 打开新会话使用 executing-plans 技能，批量执行并设置检查点

**您选择哪种方式？**
