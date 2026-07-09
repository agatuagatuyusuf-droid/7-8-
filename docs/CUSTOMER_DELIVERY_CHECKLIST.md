# 客户交付检查清单

## 交付前

- [ ] 已部署授权服务器
- [ ] 已配置 PostgreSQL
- [ ] 已配置 Nginx HTTPS
- [ ] 已配置 AUTODOOR_SERVER_PRIVATE_KEY_PATH
- [ ] 已配置 AUTODOOR_JWT_SECRET
- [ ] 已创建 Admin 后台账号
- [ ] 已创建产品 autodoor_pro
- [ ] 已创建功能列表
- [ ] 已生成客户激活码
- [ ] 已构建商业包
- [ ] 已运行 check_commercial_package
- [ ] 已运行 check_built_app_smoke

## 客户安装包

- [ ] AutoDoorPro.exe 存在
- [ ] CoreService/AutoDoor.CoreService.exe 存在
- [ ] OCRWorker/OCRWorker.exe 存在
- [ ] NOTICE.txt 存在
- [ ] THIRD_PARTY_LICENSES.txt 存在
- [ ] 无源码
- [ ] 无私钥
- [ ] 无合同授权书
- [ ] 无旧作者信息

## 客户激活

- [ ] 输入激活码成功
- [ ] 绑定机器码成功
- [ ] license.status valid=true
- [ ] OCR 功能按授权可用
- [ ] 图像匹配功能按授权可用
- [ ] 未授权功能被 C# CoreService 拒绝

## 售后

- [ ] 保存客户机器码
- [ ] 保存激活码
- [ ] 保存订单记录
- [ ] 保存授权到期时间
- [ ] 告知离线宽限期
- [ ] 告知换电脑需要解绑机器码
