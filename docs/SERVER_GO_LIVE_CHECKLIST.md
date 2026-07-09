# 授权服务器上线检查清单

## 环境变量

必须配置：

- [ ] ASPNETCORE_ENVIRONMENT=Production
- [ ] AUTODOOR_DB_PROVIDER=PostgreSQL
- [ ] AUTODOOR_DB_CONNECTION_STRING
- [ ] AUTODOOR_SERVER_PRIVATE_KEY_PATH
- [ ] AUTODOOR_JWT_SECRET
- [ ] AUTODOOR_ADMIN_USERNAME
- [ ] AUTODOOR_ADMIN_PASSWORD
- [ ] AUTODOOR_ALLOWED_ORIGINS

## 数据库

- [ ] PostgreSQL 已启动
- [ ] 数据库 autodoor 已创建
- [ ] 用户权限正确
- [ ] 数据持久化 volume 已配置
- [ ] 备份脚本已准备

## API

- [ ] /health 正常
- [ ] /ready 正常
- [ ] /api/admin/login 正常
- [ ] /api/client/activate 正常
- [ ] /api/client/heartbeat 正常
- [ ] /api/client/version/latest 正常

## 安全

- [ ] public-key endpoint 生产默认关闭
- [ ] JWT secret 不是默认值
- [ ] 没有 admin123
- [ ] 没有 TEST-ACTIVATE-123456
- [ ] 私钥未进入仓库
- [ ] 私钥未进入客户端包
- [ ] Nginx HTTPS 已配置
