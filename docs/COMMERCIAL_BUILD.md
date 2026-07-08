# 商业构建文档

## 构建流程

```bash
build_commercial.bat
```

流程：

1. 清理旧的 build/dist 目录
2. 从 build_config.json 生成构建信息
3. Python 语法检查 (compileall)
4. PyInstaller 打包 (autodoor_bt_commercial.spec)
5. 检查 dist 目录无源码泄露

## 构建产物

- 输出目录: `dist/autodoor-pro-{VERSION}/`
- 可执行文件: `autodoor-pro-{VERSION}.exe`
- 包含资源: assets, drivers, rapidocr 模型

## 注意事项

1. autodoor_bt_commercial.spec 不包含源码 .py 作为 datas
2. 构建前确保已执行 `generate_build_info.py`
3. 构建后执行 `tools/check_dist_no_source.py` 验证

## 打包工具依赖

```
pip install pyinstaller pyarmor pip-licenses
```
