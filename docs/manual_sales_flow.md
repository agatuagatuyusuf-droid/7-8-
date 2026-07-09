# 手动销售流程 — Manual Sales Flow

## 1. 客户付款
客户通过线下渠道付款后，管理员获得付款确认。

## 2. 后台创建用户
```
POST /api/admin/login → 获取 JWT Token
POST /api/admin/users → 创建用户
```

## 3. 创建订单
```
POST /api/admin/orders → 创建订单，标记已付款
```

## 4. 生成激活码
```
POST /api/admin/activation-codes/generate → 生成激活码
```
参数：ProductId, Edition, DurationDays, MachineLimit, Count

## 5. 发送给客户
将激活码通过邮件/消息发送给客户。

## 6. 客户激活
客户在软件中输入激活码，调用 `/api/client/activate`。

## 7. 机器码绑定
激活时自动绑定机器码，一个激活码只能激活一台机器（由 MachineLimit 控制）。

## 8. 续费
```
POST /api/admin/licenses/{id}/extend → 延长授权
```
Body: `{"days": 365}`

## 9. 解绑机器码
目前不支持自动解绑，需要通过后台管理。

## 10. 封禁机器码
```
POST /api/admin/machines/{id}/ban → 封禁机器
```

## 11. 强制更新
```
POST /api/admin/version-releases → 发布版本
```
设置 `ForceUpdate=true` 将强制客户端更新。
