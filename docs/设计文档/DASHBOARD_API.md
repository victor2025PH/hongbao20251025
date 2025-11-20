# Dashboard API 文档

本文档说明红包系统控制台 Dashboard 使用的 API 接口。

## API 基础地址

- **Web Admin API**: `http://localhost:8000`
- **前端地址**: `http://localhost:3001`

---

## Dashboard 统计接口

### 1. 获取统计数据（需要认证）

**接口路径**: `GET /admin/api/v1/dashboard/stats`

**认证要求**: 需要管理员登录（Session Cookie）

**响应格式**:
```json
{
  "users_total": 1234,
  "envelopes_active": 56,
  "ledger_7d_amount": "12345.67",
  "ledger_7d_count": 890,
  "recharge_pending": 12,
  "recharge_success": 345,
  "since": "2024-01-01T00:00:00",
  "until": "2024-01-08T00:00:00"
}
```

**字段说明**:
- `users_total`: 用户总数
- `envelopes_active`: 活跃红包数
- `ledger_7d_amount`: 近7天账本金额（字符串格式，如 "12345.67"）
- `ledger_7d_count`: 近7天账本条数
- `recharge_pending`: 充值待处理订单数
- `recharge_success`: 充值成功订单数
- `since`: 统计起始时间（ISO 格式）
- `until`: 统计结束时间（ISO 格式）

**后端实现**: `web_admin/controllers/dashboard.py:164` - `get_dashboard_stats()`

---

### 2. 获取统计数据（无需认证，公开接口）

**接口路径**: `GET /admin/api/v1/dashboard/stats/public`

**认证要求**: 无需认证

**响应格式**: 与认证接口相同

**特殊说明**:
- 如果数据库查询失败，此接口会返回 mock 数据，确保前端正常显示
- Mock 数据值：
  - `users_total`: 1234
  - `envelopes_active`: 56
  - `ledger_7d_amount`: "12345.67"
  - `ledger_7d_count`: 890
  - `recharge_pending`: 12
  - `recharge_success`: 345

**后端实现**: `web_admin/controllers/dashboard.py:179` - `get_dashboard_stats_public()`

---

## 认证相关接口

### 1. 检查登录状态

**接口路径**: `GET /admin/api/v1/auth/status`

**认证要求**: 无需认证

**响应格式**:
```json
{
  "ok": true,
  "authenticated": true,
  "user": {
    "username": "admin",
    "tg_id": 123456789
  }
}
```

或未登录时：
```json
{
  "ok": true,
  "authenticated": false,
  "user": null
}
```

**后端实现**: `web_admin/auth.py:508` - `get_auth_status()`

---

### 2. API 登录接口

**接口路径**: `POST /admin/api/v1/auth/login`

**认证要求**: 无需认证

**请求格式** (Form Data):
- `username`: 管理员用户名
- `password`: 管理员密码

**响应格式** (成功):
```json
{
  "ok": true,
  "message": "Login successful",
  "user": {
    "username": "admin",
    "tg_id": 123456789
  }
}
```

**响应格式** (失败):
```json
{
  "ok": false,
  "message": "Invalid username"
}
```

**状态码**:
- `200`: 登录成功
- `401`: 用户名或密码错误
- `429`: 登录尝试次数过多，账户被锁定

**后端实现**: `web_admin/auth.py:532` - `api_login()`

---

### 3. HTML 登录页面

**接口路径**: `GET /admin/login`

**认证要求**: 无需认证

**响应**: HTML 页面（用于浏览器直接访问）

**后端实现**: `web_admin/auth.py:321` - `login_form()`

---

## 前端调用逻辑

### Dashboard 数据获取流程

1. **优先尝试认证接口** (`/admin/api/v1/dashboard/stats`)
   - 如果成功，直接返回数据
   - 如果返回 401/403（未认证），进入步骤 2

2. **回退到公开接口** (`/admin/api/v1/dashboard/stats/public`)
   - 如果成功，返回数据
   - 如果失败（404/500 等），进入步骤 3

3. **使用 Mock 数据**
   - 前端使用预定义的 mock 数据，确保 UI 不会完全空白
   - 在浏览器控制台输出警告信息

### 前端实现位置

- **API 调用**: `frontend-next/src/lib/api.ts` - `getDashboardStats()`
- **Mock 数据**: `frontend-next/src/lib/api.ts` - `MOCK_DASHBOARD_STATS`
- **页面组件**: `frontend-next/src/app/page.tsx`

---

## 认证方式

### Session Cookie 认证

- 登录成功后，后端会在 Session 中存储用户信息
- 后续请求通过 Cookie 自动携带 Session 信息
- Session 键名: `SESSION_USER_KEY` (定义在 `web_admin/constants.py`)

### 环境变量配置

管理员认证相关环境变量：
- `ADMIN_WEB_USER`: 管理员用户名（默认: "admin"）
- `ADMIN_WEB_PASSWORD`: 管理员密码（明文，不推荐生产环境使用）
- `ADMIN_WEB_PASSWORD_HASH`: 管理员密码哈希（推荐，支持 sha256 或 bcrypt）
- `ADMIN_TG_ID`: 管理员 Telegram ID
- `ADMIN_SESSION_SECRET`: Session 加密密钥（至少 32 字符）

---

## Mock 数据说明

### 当前 Mock 数据值

当后端接口无法访问或数据库连接失败时，前端会使用以下 mock 数据：

```typescript
{
  users_total: 1234,
  envelopes_active: 56,
  ledger_7d_amount: '12345.67',
  ledger_7d_count: 890,
  recharge_pending: 12,
  recharge_success: 345,
  since: '2024-01-01T00:00:00.000Z',
  until: '2024-01-08T00:00:00.000Z'
}
```

### 替换为真实数据

**后端实现位置**: `web_admin/controllers/dashboard.py:37` - `_stats_query()`

该函数从数据库查询以下数据：
1. **用户总数**: 从 `User` 表统计
2. **活跃红包数**: 从 `Envelope` 表统计（状态为 OPEN/ACTIVE 或未关闭的红包）
3. **近7天账本金额/条数**: 从 `Ledger` 表统计（类型为 RECHARGE, HONGBAO_SEND, HONGBAO_GRAB, ADJUSTMENT）
4. **充值订单统计**: 从 `RechargeOrder` 表统计（PENDING 和 SUCCESS 状态）

**注意事项**:
- 如果数据库表不存在或查询失败，函数会捕获异常并返回 0
- 公开接口 (`/admin/api/v1/dashboard/stats/public`) 在数据库查询失败时会返回 mock 数据

---

## 错误处理

### 前端错误处理策略

1. **网络错误**: 自动回退到公开接口，最后使用 mock 数据
2. **404 错误**: 尝试公开接口，失败后使用 mock 数据
3. **401/403 错误**: 直接尝试公开接口
4. **500 错误**: 使用 mock 数据，显示警告信息

### 用户提示

- 如果使用 mock 数据，页面会显示提示信息
- 提供登录链接，引导用户登录以获取真实数据
- 提供"重试"按钮，允许用户手动刷新数据

---

## 未来改进计划

### 待实现功能

1. **实时数据更新**
   - 使用 WebSocket 推送数据更新
   - 或使用 Server-Sent Events (SSE)

2. **数据缓存优化**
   - 后端已实现 30 秒缓存（`_CACHE_TTL = 30`）
   - 前端可以考虑增加本地缓存

3. **更多统计指标**
   - 今日新增用户数
   - 今日红包发送数
   - 今日充值金额
   - 成功率统计

4. **任务列表接口**
   - 最近任务列表（任务 ID、类型、群组、金额、状态、时间）
   - 任务执行日志

---

## 测试建议

### 测试场景

1. **正常情况**: 后端服务运行，数据库连接正常
   - 应该返回真实数据

2. **未认证访问**: 未登录用户访问
   - 应该自动回退到公开接口
   - 如果公开接口也失败，使用 mock 数据

3. **后端服务停止**: 后端服务未运行
   - 应该使用 mock 数据
   - 显示友好的错误提示

4. **数据库连接失败**: 后端运行但数据库不可用
   - 公开接口应该返回 mock 数据
   - 认证接口可能返回 500 错误

---

## 相关文件

### 后端文件
- `web_admin/controllers/dashboard.py` - Dashboard 统计接口
- `web_admin/auth.py` - 认证相关接口
- `web_admin/deps.py` - 认证依赖（`require_admin`）

### 前端文件
- `frontend-next/src/lib/api.ts` - API 调用封装
- `frontend-next/src/app/page.tsx` - Dashboard 页面
- `frontend-next/src/api/admin.ts` - Web Admin API 客户端

---

## 更新日志

- 2024-XX-XX: 初始版本，实现基础统计接口和认证接口
- 2024-XX-XX: 添加公开接口和 mock 数据 fallback 机制

