# 🔌 API 接口测试指南

## 📋 测试概述

本指南提供 Web Admin API 和 MiniApp API 的测试方法和流程。

---

## 🌐 Web Admin API 测试

### 基础信息
- **Base URL**: `http://127.0.0.1:8000`
- **健康检查**: `http://127.0.0.1:8000/healthz`
- **API 文档**: `http://127.0.0.1:8000/docs` (Swagger UI)

### 测试步骤

#### 1. 健康检查测试

```bash
# 使用 curl
curl -X GET http://127.0.0.1:8000/healthz

# 预期响应
{"ok":true,"ts":"2025-11-15T01:42:00.000000"}
```

#### 2. 访问 API 文档

在浏览器中访问：
```
http://127.0.0.1:8000/docs
```

这将打开 Swagger UI，可以：
- 查看所有 API 端点
- 测试每个接口
- 查看请求/响应格式

#### 3. 常见 API 测试端点

##### 3.1 用户统计 API
```bash
curl -X GET "http://127.0.0.1:8000/api/stats/users?start_date=2025-01-01&end_date=2025-11-15"
```

##### 3.2 红包统计 API
```bash
curl -X GET "http://127.0.0.1:8000/api/stats/hongbao?start_date=2025-01-01&end_date=2025-11-15"
```

##### 3.3 余额统计 API
```bash
curl -X GET "http://127.0.0.1:8000/api/stats/balance?start_date=2025-01-01&end_date=2025-11-15"
```

##### 3.4 导出数据 API
```bash
curl -X GET "http://127.0.0.1:8000/api/export/users" -o users_export.csv
```

#### 4. 认证测试（如果启用）

如果 API 需要认证，需要先获取 Token：

```bash
# 登录获取 Token
curl -X POST "http://127.0.0.1:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}'

# 使用 Token 访问受保护的端点
curl -X GET "http://127.0.0.1:8000/api/protected" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📱 MiniApp API 测试

### 基础信息
- **Base URL**: `http://127.0.0.1:8080`
- **健康检查**: `http://127.0.0.1:8080/healthz`
- **API 文档**: `http://127.0.0.1:8080/docs` (Swagger UI)

### 测试步骤

#### 1. 健康检查测试

```bash
# 使用 curl
curl -X GET http://127.0.0.1:8080/healthz

# 预期响应
{"ok":true}
```

#### 2. 访问 API 文档

在浏览器中访问：
```
http://127.0.0.1:8080/docs
```

#### 3. 常见 API 测试端点

##### 3.1 用户信息 API
```bash
# 获取用户信息
curl -X GET "http://127.0.0.1:8080/api/user/info?user_id=123456"
```

##### 3.2 余额查询 API
```bash
# 查询用户余额
curl -X GET "http://127.0.0.1:8080/api/user/balance?user_id=123456"
```

##### 3.3 红包列表 API
```bash
# 获取红包列表
curl -X GET "http://127.0.0.1:8080/api/hongbao/list?user_id=123456&page=1&limit=20"
```

##### 3.4 创建红包 API
```bash
curl -X POST "http://127.0.0.1:8080/api/hongbao/create" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123456,
    "amount": 100.00,
    "count": 10,
    "message": "测试红包"
  }'
```

##### 3.5 领取红包 API
```bash
curl -X POST "http://127.0.0.1:8080/api/hongbao/claim" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123456,
    "hongbao_id": "hongbao_123"
  }'
```

##### 3.6 充值 API
```bash
curl -X POST "http://127.0.0.1:8080/api/wallet/recharge" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123456,
    "amount": 500.00,
    "payment_method": "alipay"
  }'
```

##### 3.7 提现 API
```bash
curl -X POST "http://127.0.0.1:8080/api/wallet/withdraw" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123456,
    "amount": 100.00,
    "account": "alipay_account"
  }'
```

---

## 🧪 自动化测试脚本

### Web Admin API 测试脚本

```bash
#!/bin/bash
# test_web_admin_api.sh

BASE_URL="http://127.0.0.1:8000"

echo "===================================="
echo "Web Admin API 测试"
echo "===================================="

# 1. 健康检查
echo ""
echo "1. 健康检查"
curl -s "$BASE_URL/healthz" | jq '.'
echo ""

# 2. API 文档
echo "2. API 文档地址: $BASE_URL/docs"
echo ""

# 3. 测试各个端点
echo "3. 测试统计端点..."
curl -s "$BASE_URL/api/stats/users?start_date=2025-01-01&end_date=2025-11-15" | jq '.'
echo ""

echo "测试完成"
```

### MiniApp API 测试脚本

```bash
#!/bin/bash
# test_miniapp_api.sh

BASE_URL="http://127.0.0.1:8080"

echo "===================================="
echo "MiniApp API 测试"
echo "===================================="

# 1. 健康检查
echo ""
echo "1. 健康检查"
curl -s "$BASE_URL/healthz" | jq '.'
echo ""

# 2. API 文档
echo "2. API 文档地址: $BASE_URL/docs"
echo ""

# 3. 测试各个端点
echo "3. 测试用户信息端点..."
curl -s "$BASE_URL/api/user/info?user_id=123456" | jq '.'
echo ""

echo "测试完成"
```

---

## 📊 测试检查清单

### Web Admin API
- [ ] 健康检查通过
- [ ] API 文档可访问
- [ ] 用户统计 API 正常
- [ ] 红包统计 API 正常
- [ ] 余额统计 API 正常
- [ ] 导出功能正常
- [ ] 认证功能正常（如启用）

### MiniApp API
- [ ] 健康检查通过
- [ ] API 文档可访问
- [ ] 用户信息 API 正常
- [ ] 余额查询 API 正常
- [ ] 红包列表 API 正常
- [ ] 创建红包 API 正常
- [ ] 领取红包 API 正常
- [ ] 充值 API 正常
- [ ] 提现 API 正常

---

## 🔧 故障排除

### 问题 1: 连接被拒绝
```bash
# 检查服务是否运行
docker compose ps web_admin
docker compose ps miniapp_api

# 检查端口是否开放
netstat -tlnp | grep -E "8000|8080"
```

### 问题 2: 返回 500 错误
```bash
# 查看服务日志
docker compose logs web_admin --tail 50
docker compose logs miniapp_api --tail 50
```

### 问题 3: 返回 404 错误
```bash
# 检查路由配置
curl -X GET http://127.0.0.1:8000/docs
curl -X GET http://127.0.0.1:8080/docs
```

---

## 📝 测试报告模板

```markdown
# API 测试报告

## 测试时间
2025-11-15

## Web Admin API
- 健康检查: ✅/❌
- API 文档: ✅/❌
- 测试端点: X/Y 通过

## MiniApp API
- 健康检查: ✅/❌
- API 文档: ✅/❌
- 测试端点: X/Y 通过

## 发现的问题
1. ...

## 修复情况
1. ...
```

---

## 🚀 快速测试命令

### 一键测试所有 API

```bash
# Web Admin API
curl -s http://127.0.0.1:8000/healthz && echo "✅ Web Admin API 正常" || echo "❌ Web Admin API 异常"

# MiniApp API
curl -s http://127.0.0.1:8080/healthz && echo "✅ MiniApp API 正常" || echo "❌ MiniApp API 异常"
```

