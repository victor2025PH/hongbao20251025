# 红包系统控制台（Next.js + Tailwind）

红包系统管理后台前端，运行在 `http://localhost:3001`。

## 技术栈

- **框架**: Next.js 16 (App Router)
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **UI 组件**: shadcn/ui
- **数据获取**: React Query (@tanstack/react-query)
- **HTTP 客户端**: Axios

## 功能模块

### 1. Dashboard（首页）

**路径**: `http://localhost:3001/`

**功能**:
- ✅ 6 张统计卡片（使用真实后端数据）
  - 用户总数
  - 活跃红包数
  - 近7天账本金额
  - 近7天账本条数
  - 充值待处理
  - 充值成功
- ✅ 数据趋势图（近7天）
- ✅ 最近任务列表
- ✅ 自动刷新（每30秒）
- ✅ Mock 数据降级提示（当后端不可用时）

**API**: 
- `GET /admin/api/v1/dashboard` - 主接口，需要认证，字段名与前端一致
- `GET /admin/api/v1/dashboard/public` - 公开版本，无需认证（带 mock fallback）
- `GET /admin/api/v1/dashboard/stats` - 兼容接口（旧字段名）
- `GET /admin/api/v1/dashboard/stats/public` - 兼容接口（旧字段名，公开版本）

**返回字段**:
- `user_count`: 用户总数
- `active_envelopes`: 活跃红包数
- `last_7d_amount`: 近7天账本金额
- `last_7d_orders`: 近7天账本条数
- `pending_recharges`: 充值待处理
- `success_recharges`: 充值成功
- `since`: 统计开始时间
- `until`: 统计结束时间

---

### 2. 红包任务列表

**路径**: `http://localhost:3001/tasks`

**功能**:
- ✅ 任务列表展示（表格）
- ✅ 状态筛选（全部/进行中/成功/失败）
- ✅ 搜索功能（按任务ID或群组名称）
- ✅ 分页功能
- ✅ 任务详情弹窗（查看完整信息和领取明细）
- ✅ 自动刷新（每30秒）

**API**: 
- `GET /admin/api/v1/tasks` - 任务列表（真实数据，带 mock fallback）
- `GET /admin/api/v1/tasks/{task_id}` - 任务详情（真实数据，带 mock fallback）

**查询参数**:
- `page`: 页码（默认: 1）
- `per_page`: 每页数量（默认: 20）
- `status`: 状态筛选（active/closed/failed）
- `q`: 搜索关键词（任务ID或群组名称）
- `group_id`: 群组ID筛选

**返回字段**（真实数据）:
- `items`: 任务列表
  - `id`: 任务ID
  - `type`: 任务类型（群发红包/个人红包/定时红包）
  - `group_name`: 群组名称
  - `amount`: 金额
  - `count`: 数量
  - `status`: 状态（进行中/成功/失败）
  - `created_at`: 创建时间
  - `remain_count`: 剩余数量
- `pagination`: 分页信息

**Mock Fallback**: 当接口返回 404/500 时，自动使用 `src/mock/dashboard.ts` 中的模拟数据（recent_tasks）

---

### 3. 群组列表

**路径**: `http://localhost:3001/groups`

**功能**:
- ✅ 群组列表展示（卡片式）
- ✅ 搜索功能（按名称/描述）
- ✅ 状态筛选（活跃/暂停/审核中/已移除）
- ✅ 分页功能
- ✅ 自动刷新（每30秒）

**API**: 
- `GET /admin/api/v1/group-list` - 群组列表（真实数据，带 mock fallback）

**查询参数**:
- `page`: 页码（默认: 1）
- `per_page`: 每页数量（默认: 20）
- `q`: 搜索关键词（名称或描述）
- `status`: 状态筛选（active/paused/review/removed）
- `tags`: 标签筛选（数组）

**返回字段**（真实数据）:
- `items`: 群组列表
  - `id`: 群组ID
  - `name`: 群组名称
  - `description`: 描述
  - `members_count`: 成员数
  - `tags`: 标签数组
  - `language`: 语言
  - `status`: 状态
  - `invite_link`: 邀请链接
  - `entry_reward_enabled`: 是否启用入群奖励
  - `entry_reward_points`: 入群奖励点数
  - `created_at`: 创建时间
- `pagination`: 分页信息

**Mock Fallback**: 当接口返回 404/500 时，自动使用 `src/mock/groups.ts` 中的模拟数据

---

### 4. 红包统计

**路径**: `http://localhost:3001/stats`

**功能**:
- ✅ 总体统计卡片
  - 总发送数
  - 总金额
  - 成功率
  - 平均金额
- ✅ 按类型统计（群发红包、个人红包、定时红包、活动红包）
- ✅ 24小时发送分布图
- ✅ 近7天趋势
- ✅ 自动刷新（每30秒）

**API**: 
- `GET /admin/api/v1/stats` - 红包统计（兼容接口）
- `GET /admin/api/v1/stats/overview` - 整体概览统计
- `GET /admin/api/v1/stats/tasks` - 任务维度统计
- `GET /admin/api/v1/stats/groups` - 群组维度统计

---

### 5. 日志中心

**路径**: `http://localhost:3001/logs`

**功能**:
- ✅ 日志列表展示（表格）
- ✅ 级别筛选（info/warn/error）
- ✅ 关键词搜索
- ✅ 分页功能
- ✅ 自动刷新（每30秒）

**API**: 
- `GET /admin/api/v1/logs` - 系统日志（真实数据，带 mock fallback）

**查询参数**:
- `page`: 页码（默认: 1）
- `per_page`: 每页数量（默认: 50）
- `level`: 日志级别（info/warn/error）
- `module`: 模块名称
- `start`: 开始时间（ISO 格式）
- `end`: 结束时间（ISO 格式）
- `q`: 搜索关键词

**返回字段**（真实数据）:
- `items`: 日志列表
  - `id`: 日志ID
  - `level`: 级别（info/warn/error）
  - `message`: 消息内容
  - `timestamp`: 时间戳
  - `module`: 模块名称
  - `extra`: 额外信息（可选）
- `pagination`: 分页信息

**Mock Fallback**: 当接口返回 404/500 时，自动使用 `src/mock/logs.ts` 中的模拟数据

**注意**: 当前日志接口返回空列表，实际应该从日志文件或日志数据库读取（TODO）

---

### 6. 审计日志

**路径**: `http://localhost:3001/logs/audit`

**功能**:
- ✅ 审计日志列表展示（表格）
- ✅ 类型筛选（RESET/ADJUST/RECHARGE/CLAIM等）
- ✅ 用户/币种/关键词搜索
- ✅ 分页功能
- ✅ 自动刷新（每30秒）

**API**: 
- `GET /admin/api/v1/audit` - 审计日志（真实数据，带 mock fallback）
- `GET /admin/api/v1/logs/audit` - 审计日志别名（兼容接口）

**查询参数**:
- `page`: 页码（默认: 1）
- `per_page`: 每页数量（默认: 50）
- `types`: 类型筛选（数组，如 RESET, ADJUST, RECHARGE, CLAIM 等）
- `ltype`: 类型筛选（单值，兼容旧接口）
- `user`: 用户筛选（tg_id 或 @username）
- `token`: 币种筛选（USDT/TON/POINT）
- `operator`: 操作人ID
- `min_amount`: 最小金额
- `max_amount`: 最大金额
- `start`: 开始时间（ISO 格式）
- `end`: 结束时间（ISO 格式）
- `q`: 搜索关键词

**返回字段**（真实数据）:
- `items`: 审计日志列表
  - `id`: 日志ID
  - `user_id`: 用户ID
  - `username`: 用户名
  - `type`: 操作类型
  - `token`: 币种
  - `amount`: 金额
  - `note`: 备注
  - `created_at`: 创建时间
- `pagination`: 分页信息
- `sum_amount`: 总金额

**Mock Fallback**: 当接口返回 404/500 时，自动使用 `src/mock/logs.ts` 中的模拟数据

---

### 7. 系统设置

**路径**: `http://localhost:3001/settings`

**功能**:
- ✅ 金额限制配置（单个红包最大/最小金额、每日总限额）
- ✅ 风控策略配置（频率限制、黑名单、每用户每日最大发送数）
- ✅ 通知设置（失败时通知、严重错误时通知）
- ✅ 从后端读取和更新设置
- ✅ 表单验证和错误提示
- ✅ 旧版后台入口

**API**: 
- `GET /admin/api/v1/settings` - 获取系统设置
- `PUT /admin/api/v1/settings` - 更新系统设置

---

## API 配置

### 后端地址

- **默认**: `http://localhost:8000`
- **API 前缀**: `/admin/api/v1/`

### 环境变量

- `NEXT_PUBLIC_ADMIN_API_BASE_URL`: Web Admin API 基础地址（默认: `http://localhost:8000`）

### Mock 数据

所有接口都支持 mock fallback，当接口返回 404 或 500 时，自动使用 mock 数据。

Mock 数据位置: `src/mock/`

---

## 开发命令

### 前端开发

```bash
# 进入前端目录
cd frontend-next

# 安装依赖
npm install

# 启动开发服务器（端口 3001）
npm run dev

# 构建生产版本
npm run build

# 启动生产服务器
npm start
```

### 后端开发

```bash
# 启动 FastAPI 后端服务（端口 8000）
uvicorn web_admin.main:app --host 0.0.0.0 --port 8000 --reload
```

### 同时启动两个服务

**方式一：分别启动**

1. 终端 1 - 启动后端：
```bash
uvicorn web_admin.main:app --host 0.0.0.0 --port 8000 --reload
```

2. 终端 2 - 启动前端：
```bash
cd frontend-next
npm run dev
```

**方式二：使用脚本（如果项目有 start.sh 或类似脚本）**

请参考项目根目录的启动脚本。

---

## 真实 API 接口列表

### 健康检查

- **接口**: `GET /healthz`
- **返回**: `{ "ok": true, "ts": "<ISO 时间>" }`
- **用途**: 检查后端服务是否正常运行
- **认证**: 无需认证

### Dashboard (`/`)

- **真实接口**: `GET /admin/api/v1/dashboard` 或 `/admin/api/v1/dashboard/public`
- **真实数据字段**: `user_count`, `active_envelopes`, `last_7d_amount`, `last_7d_orders`, `pending_recharges`, `success_recharges`, `since`, `until`
- **趋势数据接口**: `GET /admin/api/v1/stats?days=7` - 返回最近 N 天的趋势统计
- **Mock 数据**: `src/mock/dashboard.ts`
- **提示机制**: 使用 mock 数据时显示黄色提示条

### 任务列表 (`/tasks`)

- **真实接口**: `GET /admin/api/v1/tasks`, `GET /admin/api/v1/tasks/{task_id}`
- **真实数据字段**: `items` (任务列表), `pagination` (分页信息)
- **查询参数**: `page`, `per_page`, `status`, `q`, `group_id`
- **Mock 数据**: `src/mock/dashboard.ts` (recent_tasks)
- **提示机制**: 接口失败时自动使用 mock 数据，无额外提示（列表页面）

### 群组列表 (`/groups`)

- **真实接口**: `GET /admin/api/v1/group-list`
- **真实数据字段**: `items` (群组列表), `pagination` (分页信息)
- **查询参数**: `page`, `per_page`, `q`, `status`, `tags`
- **Mock 数据**: `src/mock/groups.ts`
- **提示机制**: 接口失败时自动使用 mock 数据，无额外提示（列表页面）

### 红包统计 (`/stats`)

- **真实接口**: 
  - `GET /admin/api/v1/stats` - 趋势统计（最近 N 天）
  - `GET /admin/api/v1/stats/overview` - 整体概览统计
  - `GET /admin/api/v1/stats/tasks` - 任务维度统计
  - `GET /admin/api/v1/stats/groups` - 群组维度统计
- **真实数据字段**: 统计数据和图表数据
- **查询参数**: `days` (趋势统计天数，默认 7)
- **Mock 数据**: `src/mock/stats.ts`
- **提示机制**: 接口失败时自动使用 mock 数据，无额外提示（统计页面）

### 日志中心 (`/logs`)

- **真实接口**: `GET /admin/api/v1/logs`
- **真实数据字段**: `items` (日志列表), `pagination` (分页信息)
- **查询参数**: `page`, `per_page`, `level`, `module`, `start`, `end`, `q`
- **Mock 数据**: `src/mock/logs.ts`
- **提示机制**: 接口失败时自动使用 mock 数据，无额外提示（列表页面）
- **注意**: 当前日志接口返回空列表，实际应该从日志文件或日志数据库读取（TODO）

### 审计日志 (`/logs/audit`)

- **真实接口**: `GET /admin/api/v1/audit` 或 `/admin/api/v1/logs/audit`
- **真实数据字段**: `items` (审计日志列表), `pagination` (分页信息), `sum_amount` (总金额)
- **查询参数**: `page`, `per_page`, `types`, `ltype`, `user`, `token`, `operator`, `min_amount`, `max_amount`, `start`, `end`, `q`
- **Mock 数据**: `src/mock/logs.ts`
- **提示机制**: 接口失败时自动使用 mock 数据，无额外提示（列表页面）

### 系统设置 (`/settings`)

- **真实接口**: `GET /admin/api/v1/settings`, `PUT /admin/api/v1/settings`
- **真实数据字段**: `amount_limits`, `risk_control`, `notifications`, `feature_flags`
- **Mock 数据**: 无（设置页面需要真实数据）
- **提示机制**: 接口失败时显示错误提示

---

## Mock Fallback 机制说明

### 工作原理

1. **优先使用真实接口**: 前端首先尝试调用真实接口（如 `GET /admin/api/v1/dashboard`）
2. **降级到公开接口**: 如果认证失败（401/403），尝试公开接口（如 `GET /admin/api/v1/dashboard/public`）
3. **最终使用 Mock 数据**: 如果所有接口都失败（404/500/网络错误），自动使用本地 mock 数据

### 触发条件

- **网络错误**: 后端服务未启动或网络不可达
- **4xx 错误**: 接口不存在（404）或认证失败（401/403）
- **5xx 错误**: 后端服务内部错误（500）

### 提示行为

- **Dashboard 页面**: 使用 mock 数据时显示黄色提示条："⚠️ 当前展示的是模拟统计数据。请确保后端服务正常运行并已登录。"
- **其他页面**: 接口失败时自动使用 mock 数据，无额外提示（列表页面正常显示 mock 数据）

---

## 项目结构

```
frontend-next/
├── src/
│   ├── app/              # Next.js App Router 页面
│   │   ├── page.tsx      # Dashboard 首页
│   │   ├── groups/       # 群组列表
│   │   ├── stats/        # 红包统计
│   │   ├── logs/         # 日志中心
│   │   └── settings/     # 系统设置
│   ├── api/              # API 客户端
│   │   ├── admin.ts      # Web Admin API 客户端
│   │   └── http.ts       # HTTP 客户端配置
│   ├── components/       # React 组件
│   │   ├── ui/           # shadcn/ui 组件
│   │   ├── layout/       # 布局组件
│   │   └── shared/       # 共享组件
│   ├── lib/              # 工具函数
│   │   └── api.ts        # API 调用封装
│   ├── mock/             # Mock 数据
│   │   ├── dashboard.ts
│   │   ├── groups.ts
│   │   ├── logs.ts
│   │   ├── stats.ts
│   │   └── user.ts
│   ├── providers/       # Context Providers
│   └── types/            # TypeScript 类型定义
└── public/               # 静态资源
```

---

## API 接口列表

### Dashboard

- `GET /admin/api/v1/dashboard` - 主接口，需要认证，字段名与前端一致
  - 返回: `{ user_count, active_envelopes, last_7d_amount, last_7d_orders, pending_recharges, success_recharges, since, until }`
- `GET /admin/api/v1/dashboard/public` - 公开版本，无需认证
  - 返回: 同上
- `GET /admin/api/v1/dashboard/stats` - 兼容接口（旧字段名），需要认证
  - 返回: `{ users_total, envelopes_active, ledger_7d_amount, ledger_7d_count, recharge_pending, recharge_success, since, until }`
- `GET /admin/api/v1/dashboard/stats/public` - 兼容接口（旧字段名），无需认证
  - 返回: 同上

### 红包任务

- `GET /admin/api/v1/tasks` - 任务列表
  - 查询参数: `page`, `per_page`, `status`, `q`, `group_id`
  - 返回: `{ items, pagination }`
- `GET /admin/api/v1/tasks/{task_id}` - 任务详情
  - 返回: `{ id, token, total_amount, total_count, claimed_amount, claimed_count, remain_amount, remain_count, created_at, closed_at, creator, lucky, claims, total_claims }`

### 群组列表

- `GET /admin/api/v1/group-list`
  - 查询参数: `page`, `per_page`, `q`, `status`
  - 返回: `{ items, pagination }`

### 日志

- `GET /admin/api/v1/logs`
  - 查询参数: `page`, `per_page`, `level`, `q`
  - 返回: `{ items, pagination }`

### 红包统计

- `GET /admin/api/v1/stats` - 红包统计（兼容接口）
  - 返回: `{ total_sent, total_amount, success_rate, avg_amount, by_type, by_hour, recent_7_days }`
- `GET /admin/api/v1/stats/overview` - 整体概览统计
  - 返回: `{ total_users, total_envelopes, total_amount, total_recharges, success_rate, avg_envelope_amount, today_stats, yesterday_stats }`
- `GET /admin/api/v1/stats/tasks` - 任务维度统计
  - 返回: `{ total_tasks, by_status, by_type, recent_7_days, avg_completion_time }`
- `GET /admin/api/v1/stats/groups` - 群组维度统计
  - 返回: `{ total_groups, active_groups, paused_groups, review_groups, removed_groups, by_language, top_groups, recent_7_days_activity }`

### 系统设置

- `GET /admin/api/v1/settings` - 获取系统设置
  - 返回: `{ amount_limits, risk_control, notifications, feature_flags }`
- `PUT /admin/api/v1/settings` - 更新系统设置
  - 请求体: `{ amount_limits?, risk_control?, notifications? }`
  - 返回: `{ success, message }`

### 用户信息

- `GET /admin/api/v1/user`
  - 返回: `{ id, username, tg_id, roles, is_admin }`

---

## Mock 数据说明

当后端接口不可用（返回 404 或 500）时，前端会自动使用 mock 数据，确保 UI 不会完全空白。

Mock 数据文件:
- `src/mock/dashboard.ts` - Dashboard 数据
- `src/mock/groups.ts` - 群组列表数据
- `src/mock/logs.ts` - 日志数据
- `src/mock/stats.ts` - 红包统计数据
- `src/mock/user.ts` - 用户信息数据

---

## 自动刷新

所有数据页面都实现了自动刷新功能，使用 React Query 的 `refetchInterval` 配置：

- **刷新间隔**: 30 秒
- **实现方式**: 轮询（Polling）

可以在系统设置页面配置自动刷新开关和刷新间隔。

---

## 错误处理

- 所有 API 调用都有错误处理
- 接口失败时自动使用 mock 数据
- 显示友好的错误提示和重试按钮
- 控制台输出警告信息（便于调试）

---

## 响应式设计

- 支持桌面端、平板和移动端
- 使用 Tailwind CSS 响应式类
- 导航栏在移动端自动折叠

---

## 浏览器支持

- Chrome/Edge (最新版本)
- Firefox (最新版本)
- Safari (最新版本)

---

## 开发注意事项

1. **端口配置**:
   - 前端: `http://localhost:3001`（Next.js 开发服务器）
   - 后端: `http://localhost:8000`（FastAPI 服务）
   - 确保两个服务同时运行，前端才能获取真实数据

2. **启动顺序**:
   - **必须先启动后端服务**（端口 8000），再启动前端服务（端口 3001）
   - 如果后端未启动，前端会自动使用 mock 数据并显示提示

3. **Mock Fallback**:
   - 如果后端接口未实现或返回错误（404/500/网络错误），前端会自动使用 mock 数据
   - Dashboard 页面会显示黄色提示条："⚠️ 当前展示的是模拟统计数据。请确保后端服务正常运行并已登录。"
   - 其他页面接口失败时自动使用 mock 数据，无额外提示
   - 所有接口都有对应的 mock 数据文件

4. **自动刷新**: 所有数据页面默认每 30 秒自动刷新一次

5. **健康检查**: 
   - 后端健康检查: `GET http://localhost:8000/healthz`
   - 返回: `{ "ok": true, "ts": "<ISO 时间>" }`
   - 前端会定期检查后端服务状态

6. **认证**: 
   - 部分接口需要认证（Cookie Session 或 JWT）
   - 如果认证失败（401/403），前端会尝试使用公开接口（`/public` 后缀）
   - 如果公开接口也失败，则使用 mock 数据

7. **API 文档**:
   - FastAPI 自动生成文档: `http://localhost:8000/docs`（如果启用）
   - 所有接口都在 `/admin/api/v1/` 路径下

---

## 数据降级策略（Mock Fallback）

### 工作原理

1. **优先使用真实接口**: 前端首先尝试调用 `GET /admin/api/v1/dashboard`（需要认证）
2. **降级到公开接口**: 如果认证失败（401/403），尝试 `GET /admin/api/v1/dashboard/public`（无需认证）
3. **最终使用 Mock 数据**: 如果所有接口都失败（404/500/网络错误），自动使用本地 mock 数据

### 提示机制

- **使用真实数据时**: 不显示任何提示
- **使用 Mock 数据时**: Dashboard 页面顶部显示黄色提示条："⚠️ 当前展示的是模拟统计数据。请确保后端服务正常运行并已登录。"

### 所有接口的 Mock Fallback

所有 API 调用都实现了 mock fallback 机制：
- Dashboard: `src/mock/dashboard.ts`
- 群组列表: `src/mock/groups.ts`
- 日志: `src/mock/logs.ts`
- 红包统计: `src/mock/stats.ts`
- 用户信息: `src/mock/user.ts`

当接口返回 404 或 500 时，前端会自动使用对应的 mock 数据，确保 UI 不会完全空白。

## 后端服务要求

- **后端地址**: `http://localhost:8000`
- **API 前缀**: `/admin/api/v1/`
- **认证方式**: Cookie Session 或 JWT（根据后端配置）

确保后端服务正常运行，前端才能获取真实数据。

## 后续改进计划

- [ ] WebSocket 实时数据推送（替代轮询）
- [ ] 更多图表类型（折线图、饼图等）
- [ ] 数据导出功能（CSV/Excel）
- [ ] 用户权限管理
- [ ] 多语言支持（i18n）
- [ ] 暗色模式切换
- [ ] 审计日志详情弹窗（显示完整 payload）

---

## 相关文档

- [Dashboard API 文档](../docs/DASHBOARD_API.md)
- [端口与服务说明](../docs/PORTS_AND_SERVICES.md)
