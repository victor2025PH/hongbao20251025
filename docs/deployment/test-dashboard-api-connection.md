# Dashboard API 连接测试指南

## 问题：前端仍然显示 mock 数据

## 验证步骤

### 1. 检查后端 API 是否正常工作

```bash
# 测试公开接口
curl http://localhost:8000/admin/api/v1/dashboard/public

# 应该返回 JSON 格式的真实数据：
# {
#   "user_count": 1,
#   "active_envelopes": 0,
#   "last_7d_amount": "13409.67",
#   ...
# }
```

### 2. 检查前端容器状态

```bash
docker compose ps frontend
# 应该显示：Up (healthy)

docker compose logs frontend --tail=20
# 检查是否有错误信息
```

### 3. 浏览器控制台检查

1. **打开浏览器开发者工具**（F12）
2. **查看 Console 标签页**：
   - 应该看到类似日志：
     ```
     [Dashboard] 尝试从后端获取真实数据...
     [Dashboard] ✅ 成功从公开接口获取真实数据: {...}
     ```
   - 如果看到错误，请记录错误信息

3. **查看 Network 标签页**：
   - 找到 `/admin/api/v1/dashboard/public` 请求
   - 检查：
     - **Status**: 应该是 `200 OK`
     - **Response**: 应该是 JSON 格式的真实数据
     - **Response Headers**: 检查 `Access-Control-Allow-Origin` 是否包含前端地址

### 4. 检查 CORS 配置

如果 Network 中看到 CORS 错误，需要检查后端 CORS 配置。

### 5. 检查 API 基础地址

在浏览器控制台执行：
```javascript
// 检查 API 基础地址
console.log('API Base URL:', process.env.NEXT_PUBLIC_ADMIN_API_BASE_URL || 'http://localhost:8000')

// 测试 API 调用
fetch('http://localhost:8000/admin/api/v1/dashboard/public')
  .then(r => r.json())
  .then(data => {
    console.log('✅ API 调用成功:', data)
  })
  .catch(err => {
    console.error('❌ API 调用失败:', err)
  })
```

### 6. 检查前端代码是否已更新

在浏览器控制台执行：
```javascript
// 检查当前页面的代码版本
// 如果看到 "尝试从后端获取真实数据..." 的日志，说明代码已更新
```

## 常见问题排查

### 问题1：API 调用返回 CORS 错误

**错误信息：**
```
Access to XMLHttpRequest at 'http://localhost:8000/admin/api/v1/dashboard/public' 
from origin 'http://localhost:3001' has been blocked by CORS policy
```

**解决方法：**
检查后端 CORS 配置，确保允许 `http://localhost:3001` 来源。

### 问题2：API 调用返回 404

**错误信息：**
```
404 Not Found
```

**解决方法：**
检查后端路由是否正确注册，访问：
```
http://localhost:8000/admin/api/v1/dashboard/public
```

### 问题3：API 调用返回 401/403

**错误信息：**
```
401 Unauthorized / 403 Forbidden
```

**解决方法：**
检查是否使用了需要认证的接口，应该使用 `/admin/api/v1/dashboard/public`（公开接口）。

### 问题4：控制台没有日志输出

**可能原因：**
- 前端代码没有更新
- 浏览器缓存了旧代码

**解决方法：**
1. 强制刷新：`Ctrl + Shift + R` 或 `Ctrl + F5`
2. 清除所有缓存并硬性重新加载
3. 使用无痕模式测试

### 问题5：仍然显示 mock 数据

**检查步骤：**
1. 查看浏览器控制台的 Network 标签页
2. 找到 `/admin/api/v1/dashboard/public` 请求
3. 检查响应内容：
   - 如果返回真实数据（user_count: 1），但页面显示 mock 数据（user_count: 1234），说明前端代码逻辑有问题
   - 如果返回错误或 404，说明后端接口有问题

## 调试命令

### 测试后端 API

```bash
# 测试公开接口
curl -v http://localhost:8000/admin/api/v1/dashboard/public

# 测试健康检查
curl -v http://localhost:8000/healthz

# 测试 CORS（从不同来源访问）
curl -v -H "Origin: http://localhost:3001" http://localhost:8000/admin/api/v1/dashboard/public
```

### 查看前端日志

```bash
# 查看前端容器日志
docker compose logs frontend --tail=50

# 查看实时日志
docker compose logs -f frontend
```

### 查看后端日志

```bash
# 查看后端容器日志
docker compose logs web_admin --tail=50

# 查看 API 请求日志
docker compose logs web_admin | grep "dashboard/public"
```

## 手动测试 API 调用

在浏览器控制台（F12 -> Console）中执行：

```javascript
// 1. 测试 API 基础地址
console.log('API Base URL:', process.env.NEXT_PUBLIC_ADMIN_API_BASE_URL || 'http://localhost:8000')

// 2. 直接调用 API
fetch('http://localhost:8000/admin/api/v1/dashboard/public')
  .then(response => {
    console.log('Response Status:', response.status)
    console.log('Response Headers:', response.headers)
    return response.json()
  })
  .then(data => {
    console.log('✅ API 数据:', data)
    console.log('user_count:', data.user_count)
    console.log('active_envelopes:', data.active_envelopes)
    
    // 验证是否为真实数据
    if (data.user_count === 1234 || data.active_envelopes === 56) {
      console.warn('⚠️ 这看起来像是 mock 数据！')
    } else {
      console.log('✅ 这是真实数据！')
    }
  })
  .catch(error => {
    console.error('❌ API 调用失败:', error)
  })

// 3. 测试前端 API 客户端
import { adminApiClient } from '@/api/admin'
adminApiClient.get('/admin/api/v1/dashboard/public')
  .then(response => {
    console.log('✅ 前端 API 客户端调用成功:', response.data)
  })
  .catch(error => {
    console.error('❌ 前端 API 客户端调用失败:', error)
  })
```

## 如果仍然无法解决

请提供以下信息：
1. **浏览器控制台完整日志**（Console 和 Network 标签页）
2. **后端 API 响应**（curl 测试结果）
3. **前端容器日志**（`docker compose logs frontend --tail=50`）
4. **Network 请求详情**（F12 -> Network -> 找到失败的请求 -> 查看 Details）

---

**最后更新：** 2025-11-16

