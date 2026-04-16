# 版本检查与 Beta 限时使用功能设计文档

**文档版本**: 1.1  
**创建日期**: 2026-04-16  
**作者**: AI Assistant  
**状态**: 设计阶段

---

## 1. 概述

### 1.1 背景

`autodoor_behavior_tree` 项目目前缺少版本检查功能，需要参考 `autodoor` 项目的实现，为其添加完整的版本检查机制。同时，针对 Beta 测试版本，需要增加强制更新和限时使用功能。

### 1.2 目标

1. 实现与 `autodoor` 项目一致的版本检查逻辑
2. 增加强制更新功能，当服务端标记需要强制更新时，客户端无法继续使用
3. 增加 Beta 限时使用功能，过期后客户端无法启动
4. 在 GUI 右上角添加"检查更新"和"工具介绍"按钮
5. 统一管理更新链接，便于后续维护

### 1.3 设计原则

- **模块化设计**: 各功能独立模块，便于维护和扩展
- **用户体验优先**: 清晰的提示信息，合理的交互流程
- **安全性**: 防止用户绕过强制更新和过期检查

---

## 2. 功能需求

### 2.1 版本检查功能

| 功能项 | 描述 | 优先级 |
|--------|------|--------|
| 自动检查 | 程序启动后延迟 2 秒自动检查更新 | 高 |
| 手动检查 | 用户点击"检查更新"按钮手动检查 | 高 |
| 版本比较 | 比较当前版本与最新版本 | 高 |
| 更新通知 | 发现新版本时显示更新弹窗 | 高 |
| 忽略版本 | 用户可选择忽略某个版本的更新提示 | 中 |

### 2.2 强制更新功能

| 功能项 | 描述 | 优先级 |
|--------|------|--------|
| 标记检测 | 从 GitHub Release body 中检测 `[FORCE_UPDATE]` 标记 | 高 |
| 强制弹窗 | 显示模态弹窗，用户只能点击"去更新" | 高 |
| 阻止使用 | 强制更新弹窗无法关闭，用户无法继续使用旧版本 | 高 |
| 缓存机制 | 联网成功检测到强制更新后，记录到配置文件，防止用户通过断网绕过 | 高 |
| 异步检查 | 更新检查与客户端启动并行执行，不阻塞用户使用 | 高 |

### 2.3 Beta 限时使用功能

| 功能项 | 描述 | 优先级 |
|--------|------|--------|
| 过期检查 | 启动时检查当前日期是否超过预设过期时间 | 高 |
| 过期弹窗 | 显示过期提示弹窗 | 高 |
| 阻止启动 | 过期后程序无法启动，点击"确定"后退出 | 高 |

### 2.4 更新链接管理

| 功能项 | 描述 | 优先级 |
|--------|------|--------|
| 统一链接管理 | 使用配置变量管理所有更新相关链接 | 高 |
| 易于维护 | 修改链接时只需修改一处配置 | 高 |

**更新链接配置**：
```python
# 更新相关链接配置
UPDATE_LINKS = {
    "tool_intro": "https://my.feishu.cn/wiki/Z2AAwPevRiavmwkFf3jcL0Emnye?from=from_copylink",
    "download": "https://my.feishu.cn/wiki/Z2AAwPevRiavmwkFf3jcL0Emnye?from=from_copylink",
    "changelog": "https://my.feishu.cn/wiki/Z2AAwPevRiavmwkFf3jcL0Emnye?from=from_copylink"
}
```

### 2.5 GUI 按钮功能

| 功能项 | 描述 | 优先级 |
|--------|------|--------|
| 检查更新按钮 | 点击触发手动更新检查 | 高 |
| 工具介绍按钮 | 点击跳转到工具介绍页面 | 高 |
| 按钮位置 | GUI 右上角，与 autodoor 项目保持一致 | 高 |

---

## 3. 架构设计

### 3.1 模块结构

```
bt_utils/
├── version_checker.py          # 版本检查模块（新增）
│   ├── UPDATE_LINKS            # 更新链接配置常量
│   │
│   ├── VersionChecker 类
│   │   ├── __init__(app, owner, repo)
│   │   ├── check_for_updates(manual=False)
│   │   ├── check_force_update() -> bool
│   │   ├── _parse_force_update_flag(release_body) -> bool
│   │   ├── _show_update_notification(data, version, url)
│   │   ├── _show_force_update_dialog(version, url)
│   │   ├── _compare_versions(current, latest) -> int
│   │   ├── _is_newer_version(latest) -> bool
│   │   ├── ignore_version(version)
│   │   ├── start_auto_check(app)
│   │   └── open_tool_intro()   # 打开工具介绍页面
│   │
│   └── BetaExpirationChecker 类
│       ├── __init__(app)
│       ├── check_expiration() -> bool
│       └── show_expiration_dialog()
```

### 3.2 类图

```
┌─────────────────────────────────────────────────────────┐
│                    VersionChecker                        │
├─────────────────────────────────────────────────────────┤
│ - app: BehaviorTreeApp                                   │
│ - owner: str                                             │
│ - repo: str                                              │
│ - current_version: str                                   │
│ - ignored_version: str                                   │
│ - GITHUB_API_URL: str                                    │
├─────────────────────────────────────────────────────────┤
│ + check_for_updates(manual: bool) -> None               │
│ + check_force_update() -> bool                           │
│ + start_auto_check(app) -> None                          │
│ - _parse_force_update_flag(body: str) -> bool           │
│ - _show_update_notification(...) -> None                │
│ - _show_force_update_dialog(...) -> None                │
│ - _compare_versions(current, latest) -> int             │
│ + ignore_version(version: str) -> None                   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                BetaExpirationChecker                     │
├─────────────────────────────────────────────────────────┤
│ - app: BehaviorTreeApp                                   │
│ - EXPIRE_DATE: str (类常量)                              │
├─────────────────────────────────────────────────────────┤
│ + check_expiration() -> bool                             │
│ + show_expiration_dialog() -> None                       │
└─────────────────────────────────────────────────────────┘
```

### 3.3 启动流程

```
程序启动
    │
    ├─→ 1. Beta 过期检查
    │       │
    │       ├─→ 已过期 → 显示过期弹窗 → 退出程序 (sys.exit(0))
    │       │
    │       └─→ 未过期 → 继续
    │
    ├─→ 2. 强制更新检查
    │       │
    │       ├─→ 需要强制更新 → 显示强制更新弹窗 → 用户点击"去更新" → 打开下载页面 → 退出程序
    │       │
    │       └─→ 无需强制更新 → 继续
    │
    ├─→ 3. 正常初始化
    │       │
    │       └─→ 创建 UI、加载配置等
    │
    └─→ 4. 普通更新检查（异步，延迟2秒）
            │
            └─→ 有新版本 → 显示普通更新弹窗（可忽略）
```

---

## 4. 详细设计

### 4.0 更新链接配置

```python
# bt_utils/version_checker.py

# 更新相关链接配置（统一管理，便于维护）
UPDATE_LINKS = {
    "tool_intro": "https://my.feishu.cn/wiki/Z2AAwPevRiavmwkFf3jcL0Emnye?from=from_copylink",
    "download": "https://my.feishu.cn/wiki/Z2AAwPevRiavmwkFf3jcL0Emnye?from=from_copylink",
    "changelog": "https://my.feishu.cn/wiki/Z2AAwPevRiavmwkFf3jcL0Emnye?from=from_copylink"
}

def open_tool_intro():
    """打开工具介绍页面"""
    import webbrowser
    webbrowser.open(UPDATE_LINKS["tool_intro"])

def open_download_page():
    """打开下载页面"""
    import webbrowser
    webbrowser.open(UPDATE_LINKS["download"])
```

**使用说明**：
- 所有更新相关的链接统一在 `UPDATE_LINKS` 字典中管理
- 修改链接时只需修改一处配置
- 提供便捷函数 `open_tool_intro()` 和 `open_download_page()`

### 4.1 VersionChecker 类

#### 4.1.1 初始化

```python
class VersionChecker:
    GITHUB_API_URL = "https://api.github.com/repos/{owner}/{repo}/releases/latest"
    
    def __init__(self, app, owner: str, repo: str):
        self.app = app
        self.owner = owner
        self.repo = repo
        self.current_version = app.version
        self.ignored_version = self._load_ignored_version()
```

#### 4.1.2 强制更新检查

```python
def check_force_update(self) -> bool:
    """检查是否需要强制更新
    
    Returns:
        True: 需要强制更新，已在内部显示弹窗
        False: 无需强制更新
    """
    try:
        url = self.GITHUB_API_URL.format(owner=self.owner, repo=self.repo)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        latest_version = data.get('tag_name', '')
        release_body = data.get('body', '')
        
        # 检查是否需要强制更新
        if self._parse_force_update_flag(release_body):
            if self._is_newer_version(latest_version):
                # 获取下载链接
                download_url = self._get_download_url(data)
                
                # 显示强制更新弹窗（阻塞）
                self._show_force_update_dialog(latest_version, download_url)
                return True
        
        return False
        
    except Exception as e:
        print(f"强制更新检查失败: {str(e)}")
        return False

def _parse_force_update_flag(self, release_body: str) -> bool:
    """解析 Release body 中的强制更新标记"""
    return '[FORCE_UPDATE]' in release_body.upper()
```

#### 4.1.3 强制更新弹窗

```python
def _show_force_update_dialog(self, latest_version: str, download_url: str):
    """显示强制更新弹窗（模态，无法关闭）"""
    import tkinter as tk
    from tkinter import ttk
    
    # 创建顶层窗口
    dialog = tk.Toplevel()
    dialog.title("需要强制更新")
    dialog.geometry("450x300")
    dialog.transient(self.app.root)
    dialog.grab_set()  # 模态窗口
    
    # 禁用关闭按钮
    dialog.protocol("WM_DELETE_WINDOW", lambda: None)
    
    # 居中显示
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() - 450) // 2
    y = (dialog.winfo_screenheight() - 300) // 2
    dialog.geometry(f"450x300+{x}+{y}")
    
    # 内容
    frame = ttk.Frame(dialog, padding="20")
    frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(frame, text="⚠️ 需要强制更新", 
              font=('Arial', 14, 'bold')).pack(pady=(0, 15))
    
    ttk.Label(frame, text=f"当前版本: {self.current_version}").pack()
    ttk.Label(frame, text=f"最新版本: {latest_version}").pack(pady=(0, 15))
    
    ttk.Label(frame, text="此版本已不再维护，请更新到最新版本以继续使用。",
              wraplength=400).pack(pady=(0, 15))
    
    # 更新按钮
    def open_download():
        import webbrowser
        webbrowser.open(download_url)
        dialog.destroy()
        self.app.root.quit()  # 退出程序
    
    ttk.Button(frame, text="去更新", command=open_download).pack(pady=10)
    
    dialog.mainloop()
```

#### 4.1.4 普通更新检查

参考 `autodoor` 项目的 `VersionChecker` 实现，包括：
- 版本比较
- 更新通知弹窗
- 忽略版本功能
- 自动检查（延迟启动）

### 4.2 BetaExpirationChecker 类

#### 4.2.1 过期检查

```python
class BetaExpirationChecker:
    EXPIRE_DATE = "2026-05-01"  # 格式: YYYY-MM-DD
    
    def __init__(self, app=None):
        self.app = app
    
    def check_expiration(self) -> bool:
        """检查是否过期
        
        Returns:
            True: 已过期
            False: 未过期
        """
        from datetime import datetime
        
        try:
            expire_date = datetime.strptime(self.EXPIRE_DATE, "%Y-%m-%d")
            current_date = datetime.now()
            
            return current_date > expire_date
        except Exception as e:
            print(f"过期检查失败: {str(e)}")
            return False
```

#### 4.2.2 过期弹窗

```python
def show_expiration_dialog(self):
    """显示过期弹窗并退出"""
    import tkinter as tk
    from tkinter import ttk
    import sys
    
    root = tk.Tk()
    root.withdraw()
    
    dialog = tk.Toplevel(root)
    dialog.title("测试版本已过期")
    dialog.geometry("400x200")
    dialog.transient(root)
    dialog.grab_set()
    
    # 禁用关闭按钮
    dialog.protocol("WM_DELETE_WINDOW", lambda: None)
    
    # 居中显示
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() - 400) // 2
    y = (dialog.winfo_screenheight() - 200) // 2
    dialog.geometry(f"400x200+{x}+{y}")
    
    # 内容
    frame = ttk.Frame(dialog, padding="20")
    frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(frame, text="⚠️ 测试版本已过期",
              font=('Arial', 14, 'bold')).pack(pady=(0, 15))
    
    ttk.Label(frame, text=f"此测试版本已于 {self.EXPIRE_DATE} 过期").pack()
    ttk.Label(frame, text="感谢您的测试！请下载最新版本继续使用。",
              wraplength=350).pack(pady=(10, 15))
    
    def on_confirm():
        dialog.destroy()
        root.destroy()
        sys.exit(0)
    
    ttk.Button(frame, text="确定", command=on_confirm).pack(pady=10)
    
    root.mainloop()
```

### 4.3 配置管理扩展

在 `SettingsManager` 中添加更新相关配置：

```python
DEFAULT_SETTINGS = {
    # ... 现有配置 ...
    "update": {
        "ignored_version": "",      # 用户忽略的版本号
        "last_check_time": "",      # 上次检查时间
        "check_interval": 86400     # 检查间隔（秒），默认24小时
    }
}
```

---

## 5. 数据流设计

### 5.1 强制更新检测流程

```
客户端启动
    │
    └─→ 调用 check_force_update()
            │
            ├─→ GET https://api.github.com/repos/{owner}/{repo}/releases/latest
            │
            ├─→ 解析响应 JSON
            │       │
            │       ├─→ tag_name: 最新版本号
            │       ├─→ body: Release 说明
            │       └─→ assets: 下载链接
            │
            ├─→ 检查 body 是否包含 [FORCE_UPDATE]
            │       │
            │       ├─→ 是 → 比较版本
            │       │       │
            │       │       └─→ 当前版本 < 最新版本 → 显示强制更新弹窗
            │       │
            │       └─→ 否 → 返回 False
            │
            └─→ 返回结果
```

### 5.2 Beta 过期检测流程

```
客户端启动
    │
    └─→ 调用 check_expiration()
            │
            ├─→ 读取硬编码的 EXPIRE_DATE
            │
            ├─→ 获取当前系统时间
            │
            ├─→ 比较: current_date > expire_date ?
            │       │
            │       ├─→ 是 → 返回 True（已过期）
            │       │
            │       └─→ 否 → 返回 False（未过期）
            │
            └─→ 如果已过期 → 调用 show_expiration_dialog() → 退出程序
```

---

## 6. UI 设计

### 6.1 强制更新弹窗

```
┌─────────────────────────────────────────────┐
│  ⚠️ 需要强制更新                              │
├─────────────────────────────────────────────┤
│                                             │
│  当前版本: V1.2.0beta                        │
│  最新版本: V1.3.0                            │
│                                             │
│  此版本已不再维护，请更新到最新版本以继续使用。  │
│                                             │
│  更新内容:                                   │
│  - 重要安全更新                              │
│  - 性能优化                                  │
│  - Bug 修复                                 │
│                                             │
├─────────────────────────────────────────────┤
│              [ 去更新 ]                      │
│          (关闭按钮被禁用)                    │
└─────────────────────────────────────────────┘
```

**交互说明**：
- 弹窗为模态窗口，无法点击其他区域
- 关闭按钮（X）被禁用
- 用户只能点击"去更新"按钮
- 点击后打开下载页面并退出程序

### 6.2 Beta 过期弹窗

```
┌─────────────────────────────────────────────┐
│  ⚠️ 测试版本已过期                            │
├─────────────────────────────────────────────┤
│                                             │
│  此测试版本已于 2026-05-01 过期               │
│                                             │
│  感谢您的测试！请下载最新版本继续使用。        │
│                                             │
├─────────────────────────────────────────────┤
│              [ 确定 ]                        │
└─────────────────────────────────────────────┘
```

**交互说明**：
- 弹窗为模态窗口
- 关闭按钮（X）被禁用
- 用户点击"确定"后程序退出

### 6.3 普通更新弹窗

参考 `autodoor` 项目的设计，包括：
- 版本信息
- 更新内容
- "查看更新"、"稍后提醒"、"忽略此版本"三个按钮

### 6.4 GUI 右上角按钮设计

**按钮布局**：

```
┌─────────────────────────────────────────────────────────────┐
│  ◉ AutoDoor Behavior Tree  V1.2.0beta    [检查更新] [工具介绍] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                      主界面内容                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**按钮设计**：

```python
# bt_gui/app.py 或相关 UI 文件

from bt_utils.version_checker import open_tool_intro

# 在右上角添加按钮
button_frame = ctk.CTkFrame(header, fg_color='transparent')
button_frame.pack(side='right', padx=10)

# 检查更新按钮
check_update_btn = ctk.CTkButton(
    button_frame, 
    text='检查更新', 
    width=80, 
    height=28,
    command=lambda: version_checker.check_for_updates(manual=True)
)
check_update_btn.pack(side='left', padx=5)

# 工具介绍按钮
tool_intro_btn = ctk.CTkButton(
    button_frame, 
    text='工具介绍', 
    width=80, 
    height=28,
    command=open_tool_intro
)
tool_intro_btn.pack(side='left', padx=5)
```

**交互说明**：
- **检查更新按钮**：点击后触发手动更新检查，显示更新结果
- **工具介绍按钮**：点击后直接打开工具介绍页面（飞书文档）
- 按钮位于 GUI 右上角，与 `autodoor` 项目保持一致的设计风格

---

## 7. 错误处理

### 7.1 网络错误

```python
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.exceptions.Timeout:
    print("版本检查超时，请检查网络连接")
    return False
except requests.exceptions.RequestException as e:
    print(f"版本检查失败: {str(e)}")
    return False
```

### 7.2 解析错误

```python
try:
    data = response.json()
except json.JSONDecodeError:
    print("版本信息解析失败")
    return False
```

### 7.3 日期解析错误

```python
try:
    expire_date = datetime.strptime(self.EXPIRE_DATE, "%Y-%m-%d")
except ValueError as e:
    print(f"过期日期格式错误: {str(e)}")
    return False  # 解析失败，默认不过期
```

---

## 8. 安全考虑

### 8.1 防止绕过

1. **Beta 过期检查**：
   - 在程序启动的最早期执行
   - 在创建主窗口之前执行
   - 使用系统时间，不依赖网络

2. **强制更新检查**：
   - 在 Beta 过期检查之后立即执行
   - 在创建主窗口之前执行
   - 弹窗禁用关闭按钮

### 8.2 时间篡改防护

Beta 过期检查使用系统时间，可能被用户篡改。但考虑到：
- Beta 版本面向测试用户，信任度较高
- 强制更新作为补充措施
- 过度防护会影响用户体验

因此，当前设计不增加额外的时间篡改防护。

---

## 9. 测试计划

### 9.1 单元测试

| 测试项 | 测试内容 | 预期结果 |
|--------|----------|----------|
| 版本比较 | 1.0.0 vs 1.0.1 | 返回 1（需要更新） |
| 版本比较 | 1.0.1 vs 1.0.0 | 返回 -1（开发版本） |
| 版本比较 | 1.0.0 vs 1.0.0 | 返回 0（版本相同） |
| 强制更新标记解析 | body 包含 [FORCE_UPDATE] | 返回 True |
| 强制更新标记解析 | body 不包含标记 | 返回 False |
| 过期检查 | 当前日期 < 过期日期 | 返回 False |
| 过期检查 | 当前日期 > 过期日期 | 返回 True |

### 9.2 集成测试

| 测试场景 | 测试步骤 | 预期结果 |
|----------|----------|----------|
| Beta 过期 | 修改 EXPIRE_DATE 为过去日期，启动程序 | 显示过期弹窗，点击确定后退出 |
| 强制更新 | 在 GitHub Release body 中添加 [FORCE_UPDATE]，启动程序 | 显示强制更新弹窗，无法关闭 |
| 普通更新 | 发布新版本，启动程序 | 延迟 2 秒后显示更新通知 |
| 忽略版本 | 点击"忽略此版本"，重启程序 | 不再显示该版本的更新提示 |

### 9.3 边界测试

| 测试项 | 测试内容 | 预期结果 |
|--------|----------|----------|
| 网络超时 | 断开网络，启动程序 | 程序正常启动，不显示更新提示 |
| API 限流 | GitHub API 限流 | 程序正常启动，记录错误日志 |
| 日期格式错误 | EXPIRE_DATE 格式错误 | 程序正常启动，默认不过期 |

---

## 10. 实施计划

### 10.1 开发任务

| 任务 | 优先级 | 预计工作量 | 依赖 |
|------|--------|------------|------|
| 创建 version_checker.py 模块 | 高 | 2小时 | 无 |
| 实现 VersionChecker 类 | 高 | 3小时 | 任务1 |
| 实现 BetaExpirationChecker 类 | 高 | 1小时 | 任务1 |
| 添加更新链接配置 | 高 | 0.5小时 | 任务1 |
| 修改 main.py 启动流程 | 高 | 1小时 | 任务2,3 |
| 添加 GUI 右上角按钮 | 高 | 1小时 | 任务2,4 |
| 扩展 SettingsManager 配置 | 中 | 0.5小时 | 无 |
| 编写单元测试 | 中 | 2小时 | 任务2,3,4,5,6,7 |
| 集成测试 | 中 | 1小时 | 任务8 |
| 文档更新 | 低 | 0.5小时 | 任务9 |

**总计**: 约 12.5 小时

### 10.2 里程碑

1. **M1 - 核心功能完成** (Day 1)
   - VersionChecker 类实现
   - BetaExpirationChecker 类实现
   - 更新链接配置
   - main.py 集成

2. **M2 - GUI 集成完成** (Day 1.5)
   - GUI 右上角按钮添加
   - 按钮功能测试

3. **M3 - 测试完成** (Day 2)
   - 单元测试
   - 集成测试
   - Bug 修复

4. **M4 - 发布准备** (Day 3)
   - 文档更新
   - 代码审查
   - 发布

---

## 11. 风险与缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| GitHub API 限流 | 用户无法检查更新 | 中 | 增加重试机制，使用缓存 |
| 用户修改系统时间绕过过期检查 | Beta 版本可继续使用 | 低 | 强制更新作为补充措施 |
| 网络问题导致无法检查更新 | 用户无法得知新版本 | 中 | 提供手动检查更新入口 |
| Release body 格式不规范 | 强制更新标记无法识别 | 低 | 文档规范，测试验证 |

---

## 12. 附录

### 12.1 GitHub Release Body 示例

```markdown
## V1.3.0 更新内容

### 新功能
- 添加强制更新功能
- 添加 Beta 限时使用功能

### 优化
- 性能优化
- UI 改进

### Bug 修复
- 修复了若干已知问题

[FORCE_UPDATE]
```

### 12.2 配置文件示例

```json
{
  "version": "1.0.0",
  "update": {
    "ignored_version": "V1.2.0",
    "last_check_time": "2026-04-16T10:30:00",
    "check_interval": 86400
  }
}
```

### 12.3 API 响应示例

```json
{
  "tag_name": "V1.3.0",
  "name": "AutoDoor Behavior Tree V1.3.0",
  "body": "## 更新内容\n...\n[FORCE_UPDATE]",
  "published_at": "2026-04-15T08:00:00Z",
  "assets": [
    {
      "name": "autodoor_bt_windows_v1.3.0.zip",
      "browser_download_url": "https://github.com/..."
    }
  ]
}
```

---

## 13. 变更历史

| 版本 | 日期 | 作者 | 变更内容 |
|------|------|------|----------|
| 1.0 | 2026-04-16 | AI Assistant | 初始版本 |
| 1.1 | 2026-04-16 | AI Assistant | 添加更新链接配置和 GUI 右上角按钮设计 |

---

**文档结束**
