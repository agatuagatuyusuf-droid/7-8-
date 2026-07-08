# AutoDoor Pro 自动化行为树系统

## 产品介绍

AutoDoor Pro 是一个功能完整、可商业发行的可视化行为树编辑与执行框架，专为 Windows 平台的自动化场景设计（应用辅助、RPA 流程等）。系统提供图形化编辑器、丰富的节点类型、脚本录制、OCR 识别、多种输入引擎等能力。

## 功能说明

- **可视化编辑器**：基于 CustomTkinter 的节点式编辑器，支持拖拽、连线、缩放、框选
- **行为树引擎**：独立线程执行，支持启动/暂停/停止/恢复
- **多 Tab 并行**：多行为树同时编辑与并行运行，独立画布/引擎/黑板
- **24 种内置节点**：开始节点 + 组合节点 + 条件节点 + 动作节点
- **黑板系统**：观察者模式的数据共享机制，节点间解耦通信
- **多格式序列化**：JSON/YAML/TXT 多格式持久化，版本化数据结构
- **撤销/重做**：Command 模式，支持 100 步历史
- **DD 虚拟键盘**：DD级硬件模拟输入，绕过大多数输入检测
- **OCR 集成**：内嵌 RapidOCR，基于 ONNX Runtime，支持中英文识别
- **脚本录制**：TXT 脚本录制与回放
- **PyInstaller 打包**：内置 DD64.dll、IbInputSimulator.dll 等驱动

## 运行环境

- Windows 操作系统
- Python 3.12 或更高版本
- Visual C++ Redistributable（OCR 功能依赖）

## 安装方法

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python main.py
```

## 版本说明

当前版本：1.6.0

## 商业授权说明

本软件为商业发行版，需获得有效授权后方可使用全部功能。未经授权使用、分发、反编译、修改均属违法行为。

## 技术支持

请联系发行方获取技术支持。

## 第三方依赖声明

本软件使用了以下第三方开源组件，这些组件的版权归其各自所有者所有：

- CustomTkinter (MIT License)
- Pillow (Historical Permission Notice)
- PyAutoGUI (BSD License)
- RapidOCR (Apache 2.0 License)
- ONNX Runtime (MIT License)
- OpenCV (Apache 2.0 License)
- NumPy (BSD License)
- 以及其他依赖项

详见 THIRD_PARTY_LICENSES.txt 文件。
