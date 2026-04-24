# 窗口绑定与文本处理功能设计文档

## 1 概述

### 1.1 背景

当前 AutoDoor 行为树系统使用绝对屏幕坐标进行操作，存在以下局限性：
- 窗口移动后，坐标失效，需要重新配置
- 无法支持多窗口操作场景
- 文本输入功能缺失，无法实现动态文本输入
- 文本提取功能缺失，无法实现基于文本内容的动态决策

### 1.2 目标

新增两个核心功能模块：
1. **窗口绑定功能**：支持节点级窗口绑定，实现相对坐标操作
2. **文本处理功能**：支持文本输入和文本提取，实现动态文本交互

### 1.3 设计原则

- **不修改现有节点**：采用新增独立节点的方式，保持向后兼容
- **复用现有架构**：遵循现有节点设计模式，保持代码风格一致
- **灵活性优先**：支持多种使用场景和配置方式

---

## 2 功能需求

### 2.1 窗口绑定功能

| 需求项 | 说明 |
|--------|------|
| 窗口绑定场景 | 前台运行（窗口可见） |
| 窗口选择方式 | 点击窗口选择 |
| 绑定范围 | 节点级绑定（每个节点可以绑定不同窗口） |
| 坐标系统 | 窗口客户区相对坐标 |
| 功能 | 窗口绑定、相对坐标采集、相对坐标点击、相对坐标移动 |

### 2.2 文本处理功能

| 需求项 | 说明 |
|--------|------|
| 文本输入方式 | 多种输入源（预设文本、黑板文本、文件文本） |
| 预设文本 | 支持多个预设文本，支持顺序执行和随机执行 |
| 文本提取范围 | 支持区域全部文本和关键词文本两种模式 |
| 功能 | 文本输入节点、文本提取节点 |

---

## 3 架构设计

### 3.1 模块划分

```
新增模块：
├── bt_utils/
│   └── window_manager.py          # 窗口管理器工具类
├── bt_nodes/
│   └── actions/
│       ├── window_bind.py         # 窗口绑定节点
│       ├── relative_mouse.py      # 相对坐标鼠标节点
│       └── text_input.py          # 文本输入节点
│   └── conditions/
│       └── text_extract.py        # 文本提取节点
└── bt_gui/
    └── bt_editor/
        └── constants.py           # 新增节点类型常量
```

### 3.2 类图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          WindowManager (工具类)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ + get_window_from_point(x, y) -> hwnd                                        │
│ + get_window_rect(hwnd) -> Tuple[int, int, int, int]                        │
│ + screen_to_client(hwnd, x, y) -> Tuple[int, int]                           │
│ + client_to_screen(hwnd, x, y) -> Tuple[int, int]                           │
│ + get_window_title(hwnd) -> str                                              │
│ + is_window_valid(hwnd) -> bool                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        WindowBindNode (动作节点)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ + window_key: str                                                            │
│ + window_title: str                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ + _execute_action(context) -> NodeStatus                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                     RelativeMouseClickNode (动作节点)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ + window_key: str                                                            │
│ + position: Tuple[int, int]                                                  │
│ + use_blackboard: bool                                                       │
│ + position_key: str                                                          │
│ + button: str                                                                │
│ + action: str                                                                │
│ + duration: int                                                              │
│ + click_count: int                                                           │
│ + click_interval: int                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ + _execute_action(context) -> NodeStatus                                     │
│ + _get_position(context) -> Tuple[int, int]                                  │
│ + _convert_to_screen_coords(hwnd, position) -> Tuple[int, int]               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                     RelativeMouseMoveNode (动作节点)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ + window_key: str                                                            │
│ + position: Tuple[int, int]                                                  │
│ + use_blackboard: bool                                                       │
│ + position_key: str                                                          │
│ + smooth: bool                                                               │
│ + duration: int                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ + _execute_action(context) -> NodeStatus                                     │
│ + _get_position(context) -> Tuple[int, int]                                  │
│ + _convert_to_screen_coords(hwnd, position) -> Tuple[int, int]               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        TextInputNode (动作节点)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ + input_mode: str                                                            │
│ + preset_texts: List[str]                                                    │
│ + execution_mode: str                                                        │
│ + blackboard_key: str                                                        │
│ + file_path: str                                                             │
│ + position: Tuple[int, int]                                                  │
│ + use_blackboard: bool                                                       │
│ + position_key: str                                                          │
│ + input_delay: int                                                           │
│ + clear_before_input: bool                                                   │
│ + save_input_text: bool                                                      │
│ + output_key: str                                                            │
│ - _current_text_index: int                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ + _execute_action(context) -> NodeStatus                                     │
│ + _get_text(context) -> str                                                  │
│ + _get_next_preset_text(context) -> str                                      │
│ + _get_random_preset_text() -> str                                           │
│ + _input_text(context, text) -> None                                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                       TextExtractNode (条件节点)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ + extract_mode: str                                                          │
│ + region: Tuple[int, int, int, int]                                          │
│ + keywords: str                                                              │
│ + language: str                                                              │
│ + preprocess_mode: str                                                       │
│ + output_key: str                                                            │
│ + save_all_text: bool                                                        │
│ + all_text_key: str                                                          │
│ + save_position: bool                                                        │
│ + position_key: str                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ + _check_condition(context) -> bool                                          │
│ + _extract_all_text(text) -> str                                             │
│ + _extract_keywords_text(text, keywords) -> str                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4 详细设计

### 4.1 窗口管理器工具类

**文件位置：** `bt_utils/window_manager.py`

**核心功能：**
- 窗口句柄获取（通过点击选择）
- 窗口信息获取（标题、位置、大小）
- 坐标转换（屏幕坐标 ↔ 窗口客户区坐标）
- 窗口状态检测（是否存在、是否可见）

**关键方法：**

```python
class WindowManager:
    """窗口管理器
    
    提供窗口句柄管理、坐标转换等功能
    """
    
    @staticmethod
    def get_window_from_point(x: int, y: int) -> Optional[int]:
        """通过屏幕坐标获取窗口句柄
        
        Args:
            x: 屏幕X坐标
            y: 屏幕Y坐标
        
        Returns:
            窗口句柄，如果失败返回 None
        """
        
    @staticmethod
    def get_window_rect(hwnd: int) -> Optional[Tuple[int, int, int, int]]:
        """获取窗口客户区矩形（相对于屏幕）
        
        Args:
            hwnd: 窗口句柄
        
        Returns:
            (left, top, right, bottom) 矩形，如果失败返回 None
        """
        
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
        
    @staticmethod
    def get_window_title(hwnd: int) -> str:
        """获取窗口标题
        
        Args:
            hwnd: 窗口句柄
        
        Returns:
            窗口标题
        """
        
    @staticmethod
    def is_window_valid(hwnd: int) -> bool:
        """检查窗口是否有效
        
        Args:
            hwnd: 窗口句柄
        
        Returns:
            窗口是否有效
        """
```

**技术实现：**
- 使用 `ctypes` 调用 Windows API
- 关键API：
  - `WindowFromPoint` - 通过坐标获取窗口句柄
  - `GetClientRect` - 获取窗口客户区矩形
  - `ClientToScreen` - 客户区坐标转屏幕坐标
  - `ScreenToClient` - 屏幕坐标转客户区坐标
  - `GetWindowText` - 获取窗口标题
  - `IsWindow` - 检查窗口是否有效

---

### 4.2 窗口绑定节点

**节点类型：** 动作节点

**功能：** 绑定目标窗口，将窗口句柄保存到黑板

**参数配置：**

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| window_key | str | 窗口句柄保存的黑板变量名 | "bound_window" |
| window_title | str | 窗口标题（可选，用于自动查找） | "" |

**执行流程：**

```
1. 如果提供了 window_title：
   - 遍历所有窗口，查找标题匹配的窗口
   - 如果找到，保存窗口句柄到黑板
   - 如果未找到，返回 FAILURE

2. 否则（等待用户点击选择）：
   - 显示提示信息
   - 等待用户点击屏幕
   - 获取点击位置的窗口句柄
   - 保存窗口句柄到黑板

3. 记录窗口信息到日志

4. 返回 SUCCESS
```

**使用示例：**

```
场景1：通过点击选择窗口
开始节点
  └─ 窗口绑定节点
      - window_key: "game_window"
      └─ 相对坐标点击节点
          - window_key: "game_window"

场景2：通过标题自动查找窗口
开始节点
  └─ 窗口绑定节点
      - window_key: "chat_window"
      - window_title: "聊天窗口"
      └─ 相对坐标点击节点
          - window_key: "chat_window"
```

---

### 4.3 相对坐标点击节点

**节点类型：** 动作节点

**功能：** 在绑定窗口的客户区内执行鼠标点击

**参数配置：**

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| window_key | str | 窗口句柄的黑板变量名 | "bound_window" |
| position | Tuple[int, int] | 相对坐标（窗口客户区坐标） | None |
| use_blackboard | bool | 是否从黑板获取位置 | False |
| position_key | str | 位置的黑板变量名 | "last_detection_position" |
| button | str | 鼠标按钮 | "left" |
| action | str | 动作类型 | "press" |
| duration | int | 按住时长（毫秒） | 100 |
| click_count | int | 点击次数 | 1 |
| click_interval | int | 点击间隔（毫秒） | 100 |

**执行流程：**

```
1. 从黑板获取窗口句柄

2. 验证窗口是否有效
   - 如果窗口无效，返回 FAILURE

3. 获取点击位置
   - 如果 use_blackboard=True，从黑板读取位置
   - 否则使用 position 参数

4. 将相对坐标转换为屏幕坐标
   - screen_pos = WindowManager.client_to_screen(hwnd, position)

5. 执行鼠标点击操作
   - context.execute_mouse_click(button, screen_pos, action, duration)

6. 返回 SUCCESS
```

**使用示例：**

```
场景1：点击固定位置
开始节点
  └─ 窗口绑定节点
      └─ 相对坐标点击节点
          - position: (100, 200)
          - button: "left"

场景2：点击检测到的位置
开始节点
  └─ 窗口绑定节点
      └─ OCR检测节点（检测按钮文字）
          └─ 相对坐标点击节点
              - use_blackboard: True
              - position_key: "last_detection_position"
```

---

### 4.4 相对坐标移动节点

**节点类型：** 动作节点

**功能：** 在绑定窗口的客户区内移动鼠标

**参数配置：**

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| window_key | str | 窗口句柄的黑板变量名 | "bound_window" |
| position | Tuple[int, int] | 相对坐标（窗口客户区坐标） | None |
| use_blackboard | bool | 是否从黑板获取位置 | False |
| position_key | str | 位置的黑板变量名 | "last_detection_position" |
| smooth | bool | 是否平滑移动 | False |
| duration | int | 移动时长（毫秒） | 300 |

**执行流程：**

```
1. 从黑板获取窗口句柄

2. 验证窗口是否有效
   - 如果窗口无效，返回 FAILURE

3. 获取目标位置
   - 如果 use_blackboard=True，从黑板读取位置
   - 否则使用 position 参数

4. 将相对坐标转换为屏幕坐标
   - screen_pos = WindowManager.client_to_screen(hwnd, position)

5. 执行鼠标移动操作
   - context.execute_mouse_move(screen_pos, smooth=smooth)

6. 返回 SUCCESS
```

---

### 4.5 文本输入节点

**节点类型：** 动作节点

**功能：** 向目标位置输入文本，支持多种输入源和执行模式

**参数配置：**

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| input_mode | str | 输入模式 | "preset" |
| preset_texts | List[str] | 预设文本列表（input_mode="preset"时使用） | [] |
| execution_mode | str | 执行模式（input_mode="preset"时使用） | "sequential" |
| blackboard_key | str | 黑板变量名（input_mode="blackboard"时使用） | "extracted_text" |
| file_path | str | 文件路径（input_mode="file"时使用） | "" |
| position | Tuple[int, int] | 输入位置（None表示当前位置） | None |
| use_blackboard | bool | 是否从黑板获取位置 | False |
| position_key | str | 位置的黑板变量名 | "last_detection_position" |
| input_delay | int | 字符输入间隔（毫秒） | 50 |
| clear_before_input | bool | 输入前是否清空 | False |
| save_input_text | bool | 是否将输入的文本保存到黑板 | False |
| output_key | str | 输入文本保存的黑板变量名 | "last_input_text" |

**输入模式说明：**

| 模式 | 说明 |
|------|------|
| preset | 从预设文本列表中选择文本输入 |
| blackboard | 从黑板读取文本 |
| file | 从文件读取文本 |

**执行模式说明（仅preset模式）：**

| 模式 | 说明 |
|------|------|
| sequential | 依次执行预设文本列表，每次执行选择下一个文本 |
| random | 随机从预设文本列表中选择一个文本执行 |

**执行流程：**

```
1. 根据输入模式获取文本内容：
   - preset模式：
     - 如果 execution_mode == "sequential"：
       - 获取当前索引（从黑板读取或初始化为0）
       - 选择 preset_texts[current_index]
       - 更新索引：(current_index + 1) % len(preset_texts)
       - 保存新索引到黑板
     - 如果 execution_mode == "random"：
       - 随机选择 preset_texts 中的一个文本
   
   - blackboard模式：
     - 从黑板读取 blackboard_key 对应的文本
   
   - file模式：
     - 读取文件内容

2. 获取输入位置（可选）

3. 移动鼠标到目标位置（如果指定了位置）

4. 可选：清空现有内容（Ctrl+A）

5. 逐字符输入文本

6. 可选：将输入的文本保存到黑板

7. 返回 SUCCESS
```

**状态管理：**

| 属性 | 说明 |
|------|------|
| _current_text_index | 当前执行的文本索引（用于顺序执行） |

**黑板变量：**

| 变量名 | 说明 |
|--------|------|
| {node_id}_text_index | 当前节点的文本索引（用于顺序执行） |
| last_input_text | 最近输入的文本（如果 save_input_text=True） |

**使用示例：**

```
场景1：依次输入多个预设文本
开始节点
  └─ 文本输入节点
      - input_mode: "preset"
      - preset_texts: ["你好", "在吗", "再见"]
      - execution_mode: "sequential"

场景2：随机输入预设文本
开始节点
  └─ 文本输入节点
      - input_mode: "preset"
      - preset_texts: ["哈哈", "嘿嘿", "呵呵"]
      - execution_mode: "random"

场景3：输入提取的文本
开始节点
  └─ 文本提取节点（提取验证码）
      └─ 文本输入节点
          - input_mode: "blackboard"
          - blackboard_key: "extracted_text"
```

---

### 4.6 文本提取节点

**节点类型：** 条件节点

**功能：** 从指定区域提取文本并保存到黑板，可用于后续文本输入或关键词检测

**参数配置：**

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| extract_mode | str | 提取模式 | "all" |
| region | Tuple[int, int, int, int] | 提取区域 | None |
| keywords | str | 关键词（extract_mode="keywords"时使用） | "" |
| language | str | OCR语言 | "简体中文" |
| preprocess_mode | str | 预处理模式 | "默认" |
| output_key | str | 提取文本保存的黑板变量名 | "extracted_text" |
| save_all_text | bool | 是否保存所有识别文本到额外变量 | False |
| all_text_key | str | 所有文本保存的黑板变量名 | "all_ocr_text" |
| save_position | bool | 是否保存检测位置 | True |
| position_key | str | 检测位置保存的黑板变量名 | "last_detection_position" |

**提取模式说明：**

| 模式 | 说明 | 输出内容 |
|------|------|----------|
| all | 提取区域内所有文本 | 完整文本字符串 |
| keywords | 仅提取包含关键词的文本行 | 匹配关键词的文本行（多行用换行符连接） |

**执行流程：**

```
1. 获取指定区域的截图

2. 执行OCR识别，获取所有文本

3. 根据提取模式处理结果：
   - all模式：
     - 直接保存所有识别文本到黑板
   
   - keywords模式：
     - 按行分割文本
     - 筛选包含关键词的行
     - 将匹配的行连接后保存到黑板

4. 可选：保存所有识别文本到额外变量

5. 可选：保存检测位置到黑板

6. 返回成功/失败状态
```

**返回值说明：**

| 情况 | 返回状态 | 黑板内容 |
|------|----------|----------|
| 成功提取文本 | SUCCESS | output_key: 提取的文本 |
| 未识别到文本 | FAILURE | output_key: 空字符串 |
| OCR识别失败 | FAILURE | output_key: 空字符串 |

**使用示例：**

```
场景1：提取验证码并输入
开始节点
  └─ 文本提取节点（提取验证码区域）
      └─ 文本输入节点（输入提取的验证码）

场景2：提取特定关键词文本
开始节点
  └─ 文本提取节点
      - extract_mode: "keywords"
      - keywords: "价格"
      └─ 变量判断节点（判断价格是否符合条件）

场景3：提取文本用于后续检测
开始节点
  └─ 文本提取节点（提取物品名称）
      └─ OCR检测节点（检测提取的名称是否存在）
```

**与现有OCR检测节点的区别：**

| 节点 | 功能 | 输出 |
|------|------|------|
| OCRConditionNode | 检测关键词是否存在 | 位置（用于点击） |
| TextExtractNode | 提取文本内容 | 文本内容（用于输入或判断） |

---

## 5 GUI设计

### 5.1 节点面板新增节点

在节点面板中新增以下节点：

**动作节点：**
- 窗口绑定节点
- 相对坐标点击节点
- 相对坐标移动节点
- 文本输入节点

**条件节点：**
- 文本提取节点

### 5.2 属性面板字段类型

新增字段类型：

| 字段类型 | 组件 | 说明 |
|----------|------|------|
| window_selector | CTkEntry + 选择按钮 | 窗口选择（点击窗口获取句柄） |
| text_list | CTkTextbox + 添加/删除按钮 | 文本列表编辑器 |

### 5.3 窗口选择交互流程

```
1. 用户点击【选择窗口】按钮
2. 鼠标变成十字形状
3. 用户点击目标窗口
4. 获取窗口句柄和标题
5. 显示窗口标题在输入框中
6. 保存窗口句柄到节点配置
```

---

## 6 数据流设计

### 6.1 窗口绑定数据流

```
用户点击窗口
    ↓
WindowManager.get_window_from_point(x, y)
    ↓
获取窗口句柄 (hwnd)
    ↓
WindowBindNode 保存到黑板
    ↓
blackboard.set(window_key, hwnd)
    ↓
RelativeMouseClickNode 读取窗口句柄
    ↓
blackboard.get(window_key)
    ↓
WindowManager.client_to_screen(hwnd, position)
    ↓
转换为屏幕坐标
    ↓
执行鼠标点击
```

### 6.2 文本处理数据流

```
文本提取节点
    ↓
OCR识别
    ↓
提取文本
    ↓
blackboard.set(output_key, text)
    ↓
文本输入节点读取文本
    ↓
blackboard.get(blackboard_key)
    ↓
输入文本
```

---

## 7 错误处理

### 7.1 窗口相关错误

| 错误场景 | 处理方式 |
|----------|----------|
| 窗口句柄无效 | 返回 FAILURE，记录日志 |
| 窗口已关闭 | 返回 FAILURE，记录日志 |
| 窗口最小化 | 返回 FAILURE，记录日志 |
| 坐标转换失败 | 返回 FAILURE，记录日志 |

### 7.2 文本输入相关错误

| 错误场景 | 处理方式 |
|----------|----------|
| 预设文本列表为空 | 返回 FAILURE，记录日志 |
| 黑板变量不存在 | 返回 FAILURE，记录日志 |
| 文件不存在 | 返回 FAILURE，记录日志 |
| 文件读取失败 | 返回 FAILURE，记录日志 |

### 7.3 文本提取相关错误

| 错误场景 | 处理方式 |
|----------|----------|
| OCR识别失败 | 返回 FAILURE，记录日志 |
| 未识别到文本 | 返回 FAILURE，记录日志 |
| 关键词未匹配 | 返回 FAILURE，记录日志 |

---

## 8 测试计划

### 8.1 单元测试

| 测试项 | 测试内容 |
|--------|----------|
| WindowManager | 窗口句柄获取、坐标转换 |
| WindowBindNode | 窗口绑定、黑板保存 |
| RelativeMouseClickNode | 相对坐标点击、坐标转换 |
| RelativeMouseMoveNode | 相对坐标移动、坐标转换 |
| TextInputNode | 多种输入模式、顺序/随机执行 |
| TextExtractNode | 全文提取、关键词提取 |

### 8.2 集成测试

| 测试场景 | 测试内容 |
|----------|----------|
| 窗口绑定 + 相对坐标点击 | 完整流程测试 |
| 文本提取 + 文本输入 | 完整流程测试 |
| 多窗口操作 | 不同窗口绑定测试 |

### 8.3 用户验收测试

| 测试场景 | 预期结果 |
|----------|----------|
| 绑定游戏窗口并点击按钮 | 成功点击按钮 |
| 提取验证码并输入 | 成功输入验证码 |
| 依次输入多个预设文本 | 按顺序输入文本 |
| 随机输入预设文本 | 随机选择文本输入 |

---

## 9 实现计划

### 9.1 开发阶段

| 阶段 | 内容 | 预计时间 |
|------|------|----------|
| 第一阶段 | WindowManager 工具类 | 1天 |
| 第二阶段 | 窗口绑定节点 | 1天 |
| 第三阶段 | 相对坐标点击/移动节点 | 1天 |
| 第四阶段 | 文本输入节点 | 1天 |
| 第五阶段 | 文本提取节点 | 1天 |
| 第六阶段 | GUI集成 | 1天 |
| 第七阶段 | 测试与修复 | 2天 |

### 9.2 依赖关系

```
WindowManager
    ↓
WindowBindNode
    ↓
RelativeMouseClickNode / RelativeMouseMoveNode
    ↓
TextInputNode
    ↓
TextExtractNode
```

---

## 10 风险评估

### 10.1 技术风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Windows API兼容性 | 中 | 使用标准API，测试多版本Windows |
| OCR识别准确率 | 中 | 提供预处理模式选项 |
| 窗口权限问题 | 低 | 提供错误提示，建议以管理员运行 |

### 10.2 用户体验风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 窗口选择交互复杂 | 中 | 提供清晰的提示信息 |
| 相对坐标概念理解困难 | 中 | 提供详细文档和示例 |
| 文本输入速度慢 | 低 | 提供输入间隔配置 |

---

## 11 总结

本设计文档详细描述了窗口绑定功能和文本处理功能的设计方案，采用新增独立节点的方式，保持向后兼容，支持灵活的使用场景。通过 WindowManager 工具类封装窗口操作，通过新增节点实现相对坐标操作和文本处理功能，满足用户的多窗口操作和动态文本交互需求。
