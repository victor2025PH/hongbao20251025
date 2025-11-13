# Dashboard 实现总结

本文档总结红包系统控制台 Dashboard 的实现过程和当前状态。

---

## 一、前端依赖的统计接口

### 已识别的接口

1. **Dashboard 统计数据接口**
   - 路径: `/admin/api/v1/dashboard/stats` (需要认证)
   - 回退路径: `/admin/api/v1/dashboard/stats/public` (无需认证)
   - 方法: `GET`
   - 响应结构: 见 `frontend-next/src/lib/api.ts` - `DashboardStats` 接口

2. **健康检查接口**
   - 路径: `/healthz`
   - 方法: `GET`
   - 用途: 检查后端服务是否正常运行

---

## 二、后端接口实现

### 已实现的接口

#### 1. Dashboard 统计接口

**文件**: `web_admin/controllers/dashboard.py`

**接口列表**:
- `GET /admin/api/v1/dashboard/stats` (需要认证)
  - 实现函数: `get_dashboard_stats()` (第 164 行)
  - 认证要求: `require_admin`
  - 数据来源: 数据库查询（`_stats_query()` 函数）

- `GET /admin/api/v1/dashboard/stats/public` (无需认证)
  - 实现函数: `get_dashboard_stats_public()` (第 179 行)
  - 认证要求: 无
  - 数据来源: 数据库查询，失败时返回 mock 数据

**返回字段**:
```python
{
    "users_total": int,           # 用户总数
    "envelopes_active": int,      # 活跃红包数
    "ledger_7d_amount": str,     # 近7天账本金额（格式: "12345.67"）
    "ledger_7d_count": int,      # 近7天账本条数
    "recharge_pending": int,     # 充值待处理
    "recharge_success": int,     # 充值成功
    "since": str,                # 统计起始时间（ISO 格式）
    "until": str                 # 统计结束时间（ISO 格式）
}
```

**Mock 数据** (数据库查询失败时):
```python
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

#### 2. 认证相关接口

**文件**: `web_admin/auth.py`

**接口列表**:
- `GET /admin/login` (HTML 页面)
  - 实现函数: `login_form()` (第 321 行)
  - 用途: 显示登录页面

- `GET /admin/api/v1/auth/status` (JSON)
  - 实现函数: `get_auth_status()` (第 508 行)
  - 用途: 检查当前登录状态

- `POST /admin/api/v1/auth/login` (JSON)
  - 实现函数: `api_login()` (第 532 行)
  - 用途: API 登录接口
  - 请求参数: `username`, `password` (Form Data)
  - 响应: `{"ok": bool, "message": str, "user": {...}}`

---

## 三、认证逻辑

### 认证方式

**Session Cookie 认证**:
- 登录成功后，用户信息存储在 Session 中
- 后续请求通过 Cookie 自动携带 Session
- Session 键名: `SESSION_USER_KEY`

### 认证流程

1. **用户登录**:
   - 前端调用 `POST /admin/api/v1/auth/login`
   - 后端验证用户名和密码
   - 验证成功后，在 Session 中存储用户信息

2. **请求认证**:
   - 需要认证的接口使用 `Depends(require_admin)`
   - `require_admin` 检查 Session 中是否存在用户信息
   - 如果未认证，返回 401 或 403

3. **登录状态检查**:
   - 前端可以调用 `GET /admin/api/v1/auth/status` 检查登录状态

### 环境变量配置

管理员认证相关环境变量：
- `ADMIN_WEB_USER`: 管理员用户名（默认: "admin"）
- `ADMIN_WEB_PASSWORD`: 管理员密码（明文，不推荐生产环境）
- `ADMIN_WEB_PASSWORD_HASH`: 管理员密码哈希（推荐，支持 sha256 或 bcrypt）
- `ADMIN_TG_ID`: 管理员 Telegram ID
- `ADMIN_SESSION_SECRET`: Session 加密密钥（至少 32 字符）

---

## 四、前端错误处理

### 实现位置

**文件**: `frontend-next/src/lib/api.ts` - `getDashboardStats()`

### 错误处理策略

1. **优先尝试认证接口** (`/admin/api/v1/dashboard/stats`)
   - 如果成功，直接返回数据
   - 如果返回 401/403，进入步骤 2

2. **回退到公开接口** (`/admin/api/v1/dashboard/stats/public`)
   - 如果成功，返回数据
   - 如果失败（404/500 等），进入步骤 3

3. **使用 Mock 数据**
   - 前端使用预定义的 mock 数据
   - 在浏览器控制台输出警告信息
   - 确保 UI 不会完全空白

### Mock 数据定义

**位置**: `frontend-next/src/lib/api.ts` - `MOCK_DASHBOARD_STATS`

```typescript
const MOCK_DASHBOARD_STATS: DashboardStats = {
  users_total: 1234,
  envelopes_active: 56,
  ledger_7d_amount: '12345.67',
  ledger_7d_count: 890,
  recharge_pending: 12,
  recharge_success: 345,
  since: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
  until: new Date().toISOString(),
}
```

### 用户提示

**位置**: `frontend-next/src/app/page.tsx`

- 如果使用 mock 数据，页面会显示提示信息
- 提供登录链接: `http://localhost:8000/admin/login`
- 提供"重试"按钮，允许用户手动刷新数据

---

## 五、测试验证

### 启动服务

1. **启动后端** (8000 端口):
   ```bash
   uvicorn web_admin.main:app --host 0.0.0.0 --port 8000
   ```

2. **启动前端** (3001 端口):
   ```bash
   cd frontend-next
   npm run dev
   ```

### 测试场景

#### 场景 1: 正常情况（后端运行，数据库正常）

1. 访问 `http://localhost:3001/`
2. 应该看到真实的统计数据（来自数据库）
3. 红色错误提示不应该出现

#### 场景 2: 未认证访问

1. 访问 `http://localhost:3001/`（未登录）
2. 应该自动回退到公开接口
3. 如果公开接口成功，显示真实数据
4. 如果公开接口失败，显示 mock 数据

#### 场景 3: 后端服务停止

1. 停止后端服务
2. 访问 `http://localhost:3001/`
3. 应该显示 mock 数据
4. 可能显示错误提示，但不应该整页空白

#### 场景 4: 数据库连接失败

1. 后端运行但数据库不可用
2. 访问 `http://localhost:3001/`
3. 公开接口应该返回 mock 数据
4. 前端应该正常显示

---

## 六、当前状态

### ✅ 已完成

1. ✅ Dashboard 统计接口（认证版本和公开版本）
2. ✅ 认证相关接口（登录状态检查、API 登录）
3. ✅ 前端错误处理和 Mock 数据 fallback
4. ✅ HTML 登录页面（`/admin/login`）
5. ✅ 文档编写

### ⚠️ 注意事项

1. **Mock 数据**: 当前使用 mock 数据作为 fallback，确保前端不会完全空白
2. **数据库查询**: 如果数据库表不存在或查询失败，会返回 0 或 mock 数据
3. **认证**: 需要管理员登录才能访问认证版本的统计接口

### 🔄 未来改进

1. **实时数据更新**: 使用 WebSocket 或 SSE 推送数据更新
2. **更多统计指标**: 今日新增用户、今日红包发送数等
3. **任务列表接口**: 最近任务列表、任务执行日志
4. **数据缓存优化**: 前端本地缓存，减少不必要的请求

---

## 七、相关文档

- [Dashboard API 文档](./DASHBOARD_API.md) - 详细的 API 接口说明
- [端口与服务说明](./PORTS_AND_SERVICES.md) - 端口分配和服务职责

---

## 八、文件清单

### 后端文件

1. `web_admin/controllers/dashboard.py`
   - `get_dashboard_stats()` - 认证版本的统计接口
   - `get_dashboard_stats_public()` - 公开版本的统计接口（带 mock fallback）

2. `web_admin/auth.py`
   - `login_form()` - HTML 登录页面
   - `get_auth_status()` - 登录状态检查接口
   - `api_login()` - API 登录接口

### 前端文件

1. `frontend-next/src/lib/api.ts`
   - `getDashboardStats()` - Dashboard 数据获取函数（带 fallback 逻辑）
   - `MOCK_DASHBOARD_STATS` - Mock 数据定义

2. `frontend-next/src/app/page.tsx`
   - Dashboard 页面组件
   - 错误处理和用户提示

3. `frontend-next/src/api/admin.ts`
   - Web Admin API 客户端配置

### 文档文件

1. `docs/DASHBOARD_API.md` - API 接口详细文档
2. `docs/DASHBOARD_IMPLEMENTATION_SUMMARY.md` - 本文档
3. `docs/PORTS_AND_SERVICES.md` - 端口和服务说明

---

## 九、快速开始

### 1. 启动后端

```bash
# 设置环境变量（如果需要）
export DATABASE_URL="sqlite:///./data.sqlite"
export FLAG_ENABLE_PUBLIC_GROUPS="true"

# 启动服务
uvicorn web_admin.main:app --host 0.0.0.0 --port 8000
```

### 2. 启动前端

```bash
cd frontend-next
npm install  # 如果还没有安装依赖
npm run dev
```

### 3. 访问 Dashboard

打开浏览器访问: `http://localhost:3001/`

### 4. 登录（可选）

如果需要访问认证版本的接口，先登录:
- 访问: `http://localhost:8000/admin/login`
- 或调用 API: `POST /admin/api/v1/auth/login`

---

## 十、问题排查

### 问题 1: Dashboard 显示 404 错误

**原因**: 后端接口路径不正确或服务未运行

**解决方案**:
1. 检查后端服务是否运行: `curl http://localhost:8000/healthz`
2. 检查接口路径: `curl http://localhost:8000/admin/api/v1/dashboard/stats/public`
3. 查看浏览器控制台的网络请求，确认实际请求的 URL

### 问题 2: Dashboard 显示 Mock 数据

**原因**: 后端接口无法访问或数据库查询失败

**解决方案**:
1. 检查后端服务是否运行
2. 检查数据库连接是否正常
3. 查看浏览器控制台的警告信息
4. 如果后端正常，尝试登录后再访问

### 问题 3: 登录后仍然显示 Mock 数据

**原因**: Session Cookie 未正确设置或携带

**解决方案**:
1. 检查浏览器是否启用了 Cookie
2. 检查 `adminApiClient` 是否配置了 `withCredentials: true`
3. 查看浏览器开发者工具的 Network 标签，确认请求是否携带 Cookie

---

## 更新日志

- 2024-XX-XX: 初始实现，完成基础统计接口和认证接口
- 2024-XX-XX: 添加公开接口和 mock 数据 fallback 机制
- 2024-XX-XX: 完善错误处理和用户提示

