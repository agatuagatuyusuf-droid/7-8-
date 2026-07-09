# AutoDoor Pro v1.6.0 正式销售版发布说明

## 版本
v1.6.0

## 分支
commercial-release-v1.6.0

## 基础提交
71aaed6

## 核心架构
- Python UI 只做界面壳
- C# CoreService 负责授权、运行时、核心节点、OCR、图像匹配
- AutoDoor.Server 负责用户、授权、机器码、封禁、版本、后台管理

## 已验证
- build_commercial.bat
- check_dist_no_source.py
- check_commercial_package.py
- check_built_app_smoke.py
- check_ocr_worker.py
- check_production_ready.py

## 可销售功能
- 行为树编辑
- 基础节点运行
- C# CoreService Runtime
- 授权激活
- 机器码绑定
- 离线缓存
- FeatureGate
- OCRWorker
- ImageConditionNode
- 商业打包
- 安装包脚本

## 需要部署后才能使用
- 授权服务器
- PostgreSQL
- Nginx HTTPS
- 生产私钥
- Admin 后台账号
- 激活码生成

## 不能宣传为已完成的内容
- 高级反破解不是绝对防破解
- C# 混淆 / 加壳 / 代码签名是预留流程，不是本仓库内已完成
- 自动支付未接入，当前是手动收费开卡

## 客户交付前必须检查
1. 授权服务器已部署
2. PostgreSQL 已备份
3. 生产私钥已配置
4. 客户端 public key 已配置
5. 安装包能启动
6. 激活码能激活
7. 未授权不能运行核心功能
8. 到期授权不能运行核心功能
