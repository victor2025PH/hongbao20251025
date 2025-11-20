# 修复红包系统控制台数据对接接口

## 修复日期
2025-11-16

## 问题描述

前端控制台（`http://localhost:3001`）显示"当前展示的是模拟统计数据"，说明前端在使用 mock 数据而不是从后端 API 获取真实数据。

## 问题分析

### 1. 前端 API 调用顺序问题

**修复前：**
- 前端优先调用 `/admin/api/v1/dashboard`（需要认证）
- 如果认证失败（401/403），才尝试 `/admin/api/v1/dashboard/public`（公开接口）
- 由于前端可能未登录，导致一直使用 mock 数据

**修复后：**
- 前端优先调用 `/admin/api/v1/dashboard/public`（公开接口，无需认证）
- 如果公开接口失败，才尝试 `/admin/api/v1/dashboard`（认证接口）
- 确保前端能够获取真实数据

### 2. 错误处理和日志不足

**修复前：**
- 错误处理不够详细
- 缺少调试日志，难以排查问题

**修复后：**
- 添加详细的日志输出
- 记录每次 API 调用的状态
- 便于调试和排查问题

## 修复方案

### 修改文件

#### ✅ `frontend-next/src/lib/api.ts`

**修改 `getDashboard()` 函数：**

1. **优先使用公开接口：**
   ```typescript
   // 首先尝试公开接口（无需认证，优先使用）
   try {
     const { data: statsData } = await adminApiClient.get<DashboardStats>('/admin/api/v1/dashboard/public')
     // 返回真实数据
     return { stats: statsData, ..., isMock: false }
   } catch (publicError) {
     // 如果公开接口失败，尝试认证接口
     // ...
   }
   ```

2. **添加详细日志：**
   - ✅ 成功获取数据时的日志
   - ⚠️ 接口失败时的警告
   - ❌ 所有接口都失败时的错误日志

3. **改进错误处理：**
   - 优先使用公开接口（无需认证）
   - 如果公开接口失败，尝试认证接口
   - 如果所有接口都失败，才使用 mock 数据

## 后端接口确认

### 接口列表

1. **公开接口（无需认证）：**
   - `GET /admin/api/v1/dashboard/public`
   - 返回格式：
     ```json
     {
       "user_count": 1,
       "active_envelopes": 0,
       "last_7d_amount": "13409.67",
       "last_7d_orders": 7,
       "pending_recharges": 0,
       "success_recharges": 0,
       "since": "2025-11-09T00:37:08.346865",
       "until": "2025-11-16T00:37:08.358083"
     }
     ```

2. **认证接口（需要登录）：**
   - `GET /admin/api/v1/dashboard`
   - 返回格式与公开接口相同

3. **健康检查：**
   - `GET /healthz`
   - 返回：`{"ok": true, "ts": "..."}`

### 接口测试

```bash
# 测试公开接口
curl http://localhost:8000/admin/api/v1/dashboard/public

# 测试健康检查
curl http://localhost:8000/healthz
```

## 验证步骤

### 1. 检查前端容器状态

```bash
docker compose ps frontend
# 应该显示：Up (healthy)
```

### 2. 检查后端 API 接口

```bash
# 测试公开接口
curl http://localhost:8000/admin/api/v1/dashboard/public

# 应该返回 JSON 格式的真实数据
```

### 3. 检查前端浏览器控制台

1. 打开 `http://localhost:3001`
2. 按 F12 打开开发者工具
3. 查看 Console 标签页
4. 应该看到类似日志：
   ```
   [Dashboard] 尝试从后端获取真实数据...
   [Dashboard] ✅ 成功从公开接口获取真实数据: {...}
   [Dashboard] ✅ 成功获取趋势数据
   ```

### 4. 验证页面显示

- ✅ **不应该**显示黄色警告："⚠️ 当前展示的是模拟统计数据"
- ✅ **应该**显示真实的统计数据：
  - 用户总数：1（真实数据）
  - 活跃红包数：0（真实数据）
  - 近7天账本金额：¥13409.67（真实数据）
  - 近7天账本条数：7（真实数据）

## 预期结果

### 修复前：
- 页面显示黄色警告："⚠️ 当前展示的是模拟统计数据"
- 统计数据为 mock 数据（用户总数：1234，活跃红包数：56 等）

### 修复后：
- **不显示**黄色警告（表示使用的是真实数据）
- 统计数据为后端返回的真实数据
- 每30秒自动刷新数据（`refetchInterval: 30000`）

## 数据实时性

- **自动刷新：** 前端每 30 秒自动刷新数据（`refetchInterval: 30000`）
- **手动刷新：** 点击页面上的"刷新数据"按钮
- **红包活动实时显示：** 
  - `active_envelopes` 字段显示当前进行中的红包数量
  - `last_7d_amount` 和 `last_7d_orders` 显示近7天的流水数据
  - 这些数据都会实时更新

## 故障排查

### 问题1：仍然显示 mock 数据

**原因：** 
- 前端容器未重启
- 浏览器缓存了旧代码
- API 接口不可用

**解决方法：**
```bash
# 重启前端容器
docker compose restart frontend

# 清理浏览器缓存
# Chrome: Ctrl + Shift + Delete

# 检查后端 API
curl http://localhost:8000/admin/api/v1/dashboard/public
```

### 问题2：控制台显示错误

**检查步骤：**
1. 打开浏览器控制台（F12）
2. 查看 Network 标签页
3. 找到 `/admin/api/v1/dashboard/public` 请求
4. 检查请求状态和响应

**常见错误：**
- **401/403：** 认证问题（应该使用公开接口）
- **404：** 接口不存在（检查后端路由）
- **500：** 后端错误（检查后端日志）
- **CORS：** 跨域问题（检查后端 CORS 配置）

### 问题3：数据不更新

**检查步骤：**
1. 确认后端数据是否变化
2. 检查后端缓存 TTL（默认 60 秒）
3. 手动刷新页面或等待 30 秒自动刷新

## 相关文件

### 修改的文件
1. `frontend-next/src/lib/api.ts` - 修复 `getDashboard()` 函数

### 相关后端文件
1. `web_admin/controllers/dashboard.py` - 后端 API 接口
2. `web_admin/main.py` - 路由注册

## 注意事项

1. **公开接口安全：** 公开接口仅返回基础统计数据，不包含敏感信息
2. **数据缓存：** 后端有 60 秒缓存，数据可能不是实时的（但足够及时）
3. **趋势数据：** 趋势数据接口可能需要认证，如果失败会使用 mock 数据（不影响主要统计）

## 修复完成状态

- ✅ 前端优先使用公开接口获取真实数据
- ✅ 添加详细日志输出
- ✅ 改进错误处理逻辑
- ✅ 后端接口正常工作
- ✅ 前端容器已重启

**修复完成时间：** 2025-11-16

