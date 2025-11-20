# 系统架构说明

本文档提供 037 红包系统管理后台的整体架构说明，帮助新同事快速了解系统组成、分层结构和数据流。

> **参考文档**: 详细文件结构请参考 `PROJECT_STRUCTURE.md`，API 接口请参考 `037_API_TABLE.md`，部署指南请参考 `037_DEPLOY_GUIDE.md`。

---

## 目录

- [系统概览](#系统概览)
- [服务组件与端口](#服务组件与端口)
- [后端分层结构](#后端分层结构)
- [前端架构](#前端架构)
- [数据流与典型请求流程](#数据流与典型请求流程)
- [存储与外部依赖](#存储与外部依赖)
- [监控、日志与告警](#监控日志与告警)
- [部署视图](#部署视图)

---

## 系统概览

037 红包系统管理后台是一个基于 Telegram 生态的综合性红包管理系统。系统核心功能包括：**Telegram Bot 红包发送与领取**、**Web 管理后台**（HTML 页面 + REST API）、**MiniApp 后端 API**（支持 Telegram MiniApp 前端）、以及**现代化的 Next.js 控制台前端**。

这是一个「一套后端，多入口」的架构设计：

- **Telegram Bot** (`app.py`): 用户通过 Telegram 与机器人交互，发送红包、领取红包、查询余额等
- **Web Admin** (`web_admin/main.py`): 提供传统的 HTML 管理界面，管理员可以查看数据、审核群组、管理订单等
- **MiniApp API** (`miniapp/main.py`): 为 Telegram MiniApp 提供 REST API，支持公开群组创建、活动管理等
- **Next.js 前端控制台** (`frontend-next/`): 现代化的管理控制台，提供 Dashboard、任务管理、统计图表等可视化界面

所有服务共享同一套数据库（SQLite/PostgreSQL/MySQL），通过 SQLAlchemy ORM 访问，业务逻辑集中在 `services/` 层，确保数据一致性和代码复用。

---

## 服务组件与端口

| 服务 | 入口文件 | 端口 | 技术栈 | 主要能力 | 调用方 |
|------|----------|------|--------|----------|--------|
| **Telegram Bot** | `app.py` | - | aiogram 3.x | 处理用户命令、发送红包、管理群组 | Telegram 用户 |
| **Web Admin** | `web_admin/main.py` | 8000 | FastAPI + Jinja2 | HTML 管理界面、REST API、统计数据 | 管理员（浏览器）、前端控制台、Telegram Bot |
| **MiniApp API** | `miniapp/main.py` | 8080 | FastAPI | MiniApp REST API、JWT 认证、公开群组管理 | Telegram MiniApp、前端控制台 |
| **前端控制台** | `frontend-next/` | 3001 | Next.js + Tailwind + shadcn/ui | Dashboard、任务管理、统计图表、系统设置 | 管理员（浏览器） |
| **SaaS Demo** | `saas-demo/` | 3000 | Next.js | 聊天 AI 控制台（示例项目，参考用） | - |
| **miniapp-frontend** | `miniapp-frontend/` | - | Vite + React | 旧版前端（已弃用，仅作参考） | - |

### 服务职责说明

**Telegram Bot** (`app.py`):
- 使用 aiogram 框架处理 Telegram 消息和回调
- 提供红包发送、领取、余额查询、充值等用户命令
- 处理公开群组相关操作（创建、加入、审核）
- 通过 HTTP 调用 Web Admin API 获取数据或执行操作

**Web Admin** (`web_admin/main.py`, 端口 8000):
- 提供 HTML 管理界面（使用 Jinja2 模板渲染）
- 提供 REST API 接口（`/admin/api/v1/*`）
- 处理红包任务管理、充值订单、用户管理、公开群组审核等
- 提供统计数据、审计日志、系统设置等管理功能
- 处理 NowPayments IPN 回调

**MiniApp API** (`miniapp/main.py`, 端口 8080):
- 提供 Telegram MiniApp 后端 API（`/v1/*`）
- 使用 JWT Token 认证（通过 `/api/auth/login` 获取）
- 处理公开群组创建、加入、活动管理等
- 支持用户收藏、历史记录、事件追踪等功能

**前端控制台** (`frontend-next/`, 端口 3001):
- 使用 Next.js App Router 构建单页应用
- 提供现代化的管理界面（Dashboard、任务列表、群组管理、统计图表等）
- 通过 HTTP 调用 Web Admin 和 MiniApp API 获取数据
- 实现 mock fallback 机制，后端不可用时自动使用本地 mock 数据

---

## 后端分层结构

后端采用经典的分层架构，从下到上依次为：**数据模型层** → **业务服务层** → **控制器/路由层**。

### 数据模型层 (`models/`)

**职责**: 定义数据库表结构和 ORM 模型

**主要模型**:
- `models/user.py`: 用户模型（Telegram ID、余额、积分等）
- `models/envelope.py`: 红包模型（金额、数量、状态、领取记录等）
- `models/ledger.py`: 账本模型（流水记录，记录所有余额变动）
- `models/recharge.py`: 充值订单模型（订单状态、支付信息等）
- `models/public_group.py`: 公开群组模型（群组信息、活动、报告等）
- `models/invite.py`: 邀请模型（邀请关系、奖励记录等）
- `models/cover.py`: 封面模型（红包封面图片和元数据）

**数据库连接**: `models/db.py` 提供 SQLAlchemy Engine、Session、Base 类，支持 SQLite、PostgreSQL、MySQL。

**调用关系**: 所有模型通过 `models/db.py` 的 `init_db()` 函数初始化，业务服务层通过 SQLAlchemy Session 操作模型。

---

### 业务服务层 (`services/`)

**职责**: 封装业务逻辑，提供可复用的业务函数

**主要服务**:
- `services/hongbao_service.py`: 红包服务（创建红包、领取红包、关闭红包）
- `services/recharge_service.py`: 充值服务（创建订单、处理 IPN 回调、更新订单状态）
- `services/public_group_service.py`: 公开群组服务（创建群组、风险评估、状态管理）
- `services/public_group_activity.py`: 群组活动服务（创建活动、管理活动、生成报告）
- `services/public_group_tracking.py`: 群组追踪服务（事件记录、数据统计、用户历史）
- `services/ai_service.py`: AI 服务（调用 OpenAI/OpenRouter 生成内容）
- `services/ai_activity_generator.py`: AI 活动生成器（生成活动文案、规则等）
- `services/invite_service.py`: 邀请服务（处理邀请奖励）
- `services/export_service.py`: 导出服务（CSV、Excel 导出）
- `services/sheet_users.py`: Google Sheet 用户服务（同步用户数据到 Google Sheet）
- `services/google_logger.py`: Google 日志服务（记录日志到 Google）

**调用关系**: 
- 控制器层（`web_admin/controllers/`、`routers/`）调用服务层函数
- 服务层函数操作数据模型（通过 SQLAlchemy Session）
- 服务层可以调用其他服务（如 `public_group_service` 可能调用 `ai_service`）

**特点**: 
- 服务层函数通常是无状态的，接收 Session 作为参数
- 业务逻辑集中，便于测试和维护
- 支持事务管理（通过 Session 的 commit/rollback）

---

### 控制器/路由层

#### Web Admin 控制器 (`web_admin/controllers/`)

**职责**: 处理 HTTP 请求，调用服务层，返回 HTML 或 JSON

**主要控制器**:
- `web_admin/controllers/dashboard.py`: Dashboard 页面和 API（统计数据）
- `web_admin/controllers/envelopes.py`: 红包任务管理（任务列表、详情）
- `web_admin/controllers/stats.py`: 统计接口（趋势、概览、任务、群组统计）
- `web_admin/controllers/logs.py`: 系统日志 API
- `web_admin/controllers/audit.py`: 审计日志（操作记录）
- `web_admin/controllers/public_groups.py`: 公开群组管理（列表、状态、活动、AI 生成）
- `web_admin/controllers/recharge.py`: 充值订单管理
- `web_admin/controllers/settings.py`: 系统设置（金额限制、风控、通知）
- `web_admin/controllers/users.py`: 用户管理
- `web_admin/controllers/ipn.py`: NowPayments IPN 处理

**调用关系**:
- 控制器接收 HTTP 请求（FastAPI Router）
- 控制器调用服务层函数（如 `hongbao_service.create_envelope()`）
- 控制器返回 HTML（使用 Jinja2 模板）或 JSON（REST API）

---

#### MiniApp API (`miniapp/`)

**职责**: 提供 MiniApp REST API，处理认证和业务逻辑

**主要模块**:
- `miniapp/main.py`: FastAPI 应用入口，定义所有 `/v1/*` 路由
- `miniapp/auth.py`: 认证接口（Telegram code 登录、密码登录，返回 JWT Token）
- `miniapp/security.py`: JWT 安全（生成、验证、黑名单管理）
- `miniapp/middleware.py`: JWT 认证中间件（自动验证 Token 并注入用户信息）

**调用关系**:
- MiniApp API 直接操作数据模型（通过 SQLAlchemy Session）
- 部分复杂逻辑调用服务层（如 `public_group_service.create_group()`）
- 返回 JSON 响应（Pydantic 模型序列化）

---

#### Telegram Bot 路由 (`routers/`)

**职责**: 处理 Telegram 消息和回调，调用服务层，发送回复

**主要路由**:
- `routers/hongbao.py`: 红包相关命令（发送、领取、排行榜）
- `routers/envelope.py`: 红包操作（查看详情、分享等）
- `routers/balance.py`: 余额查询
- `routers/recharge.py`: 充值相关命令
- `routers/invite.py`: 邀请相关命令
- `routers/public_group.py`: 公开群组相关命令
- `routers/admin.py`: 管理员命令
- `routers/menu.py`: 菜单命令

**调用关系**:
- Bot 路由接收 Telegram 消息/回调（aiogram Router）
- Bot 路由调用服务层函数（如 `hongbao_service.create_envelope()`）
- Bot 路由通过 aiogram Bot 发送回复消息

---

### 配置与核心模块

#### 配置模块 (`config/`)

**职责**: 管理环境变量和全局配置

- `config/settings.py`: 从环境变量读取所有配置（BOT_TOKEN、DATABASE_URL、API 密钥等）
- `config/feature_flags.py`: 功能开关配置（启用/禁用特定功能）
- `config/load_env.py`: 环境变量加载（从 `.env` 文件读取）

**使用方式**: 所有模块通过 `from config.settings import settings` 访问配置。

---

#### 核心模块 (`core/`)

**职责**: 提供核心功能支持

- `core/i18n/`: 国际化模块
  - `core/i18n/i18n.py`: i18n 核心（翻译加载、获取）
  - `core/i18n/messages/`: 翻译文件目录（支持 12 种语言：zh、en、de、es、fil、fr、hi、id、ms、pt、th、vi）
- `core/middlewares/`: 中间件模块
  - `core/middlewares/errors.py`: 错误处理中间件
  - `core/middlewares/throttling.py`: 限流中间件
  - `core/middlewares/user_bootstrap.py`: 用户引导中间件
  - `core/middlewares/anti_echo.py`: 防回显中间件
- `core/clients/`: 外部客户端
  - `core/clients/nowpayments.py`: NowPayments 支付客户端（创建订单、查询状态）
- `core/utils/`: 工具函数
  - `core/utils/keyboards.py`: 键盘工具（生成 Inline Keyboard）

---

## 前端架构

### 技术栈

- **框架**: Next.js 16 (App Router)
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **UI 组件**: shadcn/ui（基于 Radix UI）
- **数据获取**: React Query (@tanstack/react-query)
- **HTTP 客户端**: Axios

### 页面路由结构

所有页面位于 `frontend-next/src/app/` 目录，使用 Next.js App Router 的文件系统路由：

| 路由 | 文件 | 说明 |
|------|------|------|
| `/` | `app/page.tsx` | Dashboard 首页（统计卡片、趋势图、任务列表） |
| `/tasks` | `app/tasks/page.tsx` | 任务列表页（红包发送任务，支持搜索、筛选、分页） |
| `/groups` | `app/groups/page.tsx` | 群组列表页（公开群组，支持搜索、筛选、分页） |
| `/groups/[id]` | `app/groups/[id]/page.tsx` | 群组详情页（动态路由） |
| `/stats` | `app/stats/page.tsx` | 红包统计页（统计图表） |
| `/logs` | `app/logs/page.tsx` | 日志中心（系统日志） |
| `/logs/audit` | `app/logs/audit/page.tsx` | 审计日志页（操作记录，支持筛选、搜索） |
| `/settings` | `app/settings/page.tsx` | 系统设置页（金额限制、风控、通知） |
| `/demo` | `app/demo/page.tsx` | Demo 页面（组件展示，参考用） |

**布局**: `app/layout.tsx` 提供根布局，包含全局导航栏（Navbar）和 Providers（React Query、Auth）。

---

### API 调用封装

前端使用分层 API 封装：

1. **HTTP 客户端基础** (`src/api/http.ts`):
   - 配置 Axios 实例（baseURL、超时、拦截器）
   - 处理请求/响应转换

2. **API 客户端实例**:
   - `src/api/admin.ts`: Web Admin API 客户端（端口 8000，`/admin/api/v1/*`）
   - `src/api/miniapp.ts`: MiniApp API 客户端（端口 8080，`/v1/*`）

3. **业务 API 封装** (`src/lib/api.ts`):
   - 封装所有业务 API 调用函数（`getDashboard()`、`getTasks()`、`getGroupList()` 等）
   - 实现 **mock fallback 机制**：接口失败时自动使用 mock 数据
   - 统一的错误处理和类型定义

**Mock Fallback 机制**:
- 所有 API 调用通过 `apiCallWithMock()` 函数包装
- 当接口返回 404/500 或网络错误时，自动使用对应的 mock 数据（`src/mock/*.ts`）
- Dashboard 页面使用 mock 数据时会显示黄色提示条"当前展示的是模拟统计数据"

---

### 组件架构

**布局组件** (`src/components/layout/`):
- `Navbar.tsx`: 全局导航栏（Dashboard、任务列表、群组、统计、日志、设置）

**共享业务组件** (`src/components/shared/`):
- `GroupCard.tsx`: 群组卡片组件
- `ActivityCard.tsx`: 活动卡片组件
- `LoadingSkeleton.tsx`: 加载骨架屏
- `ErrorNotice.tsx`: 错误提示组件

**UI 基础组件** (`src/components/ui/`):
- shadcn/ui 组件库的基础组件（Card、Button、Table、Dialog 等）

**Hooks** (`src/hooks/`):
- `usePublicGroups.ts`: 公开群组数据获取 Hook（基于 React Query）
- `useTelegramWebApp.ts`: Telegram WebApp Hook

---

### 前端与后端的关系

前端控制台主要面向**运营/管理员**使用，提供可视化的管理界面：

- **数据展示**: 通过调用 Web Admin API 和 MiniApp API 获取数据，展示在 Dashboard、任务列表、群组列表等页面
- **操作执行**: 通过 API 调用执行操作（如更新系统设置、审核群组等）
- **实时性**: 使用 React Query 的自动刷新功能（`refetchInterval`），定期更新数据
- **容错性**: 通过 mock fallback 机制，确保后端不可用时前端仍可正常展示（用于演示或开发）

---

## 数据流与典型请求流程

### 流程 1: 管理员在 Dashboard 查看统计

```
1. 管理员访问 http://localhost:3001/
   ↓
2. Next.js 前端渲染 Dashboard 页面 (app/page.tsx)
   ↓
3. 页面组件调用 getDashboard() (src/lib/api.ts)
   ↓
4. API 封装层调用 adminApiClient.get('/admin/api/v1/dashboard') (src/api/admin.ts)
   ↓
5. HTTP 请求发送到 http://localhost:8000/admin/api/v1/dashboard
   ↓
6. Web Admin 路由处理 (web_admin/controllers/dashboard.py)
   ↓
7. 控制器调用 _stats_query() 函数，查询数据库
   ↓
8. 数据库查询 (models/user.py, models/envelope.py, models/ledger.py, models/recharge.py)
   ↓
9. 聚合统计数据返回给控制器
   ↓
10. 控制器返回 JSON 响应
   ↓
11. 前端接收数据，更新 UI（显示统计卡片、趋势图）
```

**如果后端不可用**:
- 前端自动使用 `src/mock/dashboard.ts` 中的 mock 数据
- 页面显示黄色提示条"当前展示的是模拟统计数据"

---

### 流程 2: 用户在 Telegram 里发送红包命令

```
1. 用户在 Telegram 发送命令（如 /send 或点击"发红包"按钮）
   ↓
2. Telegram Bot 接收消息 (app.py)
   ↓
3. aiogram Router 匹配命令 (routers/hongbao.py)
   ↓
4. 路由处理函数调用 hongbao_service.create_envelope() (services/hongbao_service.py)
   ↓
5. 服务层函数：
   - 检查用户余额
   - 扣减余额（update_balance）
   - 创建 Envelope 记录 (models/envelope.py)
   - 写入 Ledger 流水 (models/ledger.py)
   ↓
6. 服务层返回 envelope_id
   ↓
7. 路由处理函数通过 aiogram Bot 发送红包消息到目标群组
   ↓
8. 用户点击"立即抢"按钮
   ↓
9. 路由处理函数调用 hongbao_service.grab_envelope()
   ↓
10. 服务层函数：
    - 检查红包状态和剩余数量
    - 随机分配金额
    - 增加用户余额
    - 创建 GrabRecord 记录
    - 写入 Ledger 流水
   ↓
11. 路由处理函数发送领取结果消息
   ↓
12. 管理员可以在 Web Admin 或前端控制台查看红包记录和流水
```

---

### 流程 3: 公开群组数据流

**场景 A: MiniApp 用户创建公开群组**

```
1. 用户在 Telegram MiniApp 中创建群组
   ↓
2. MiniApp 前端调用 POST /v1/groups/public (miniapp/main.py)
   ↓
3. MiniApp API 验证 JWT Token (miniapp/middleware.py)
   ↓
4. API 处理函数调用 public_group_service.create_group() (services/public_group_service.py)
   ↓
5. 服务层函数：
   - 检查用户余额（创建群组需要消耗星星）
   - 扣减余额
   - 风险评估（检查邀请链接、名称等）
   - 创建 PublicGroup 记录 (models/public_group.py)
   - 写入 Ledger 流水
   ↓
6. 返回群组信息和风险评分
   ↓
7. MiniApp 前端显示创建结果
```

**场景 B: 管理员在控制台查看群组列表**

```
1. 管理员访问 http://localhost:3001/groups
   ↓
2. Next.js 前端调用 getGroupList() (src/lib/api.ts)
   ↓
3. API 封装层调用 adminApiClient.get('/admin/api/v1/group-list') (src/api/admin.ts)
   ↓
4. HTTP 请求发送到 http://localhost:8000/admin/api/v1/group-list
   ↓
5. Web Admin 路由处理 (web_admin/controllers/public_groups.py)
   ↓
6. 控制器查询 PublicGroup 模型 (models/public_group.py)
   ↓
7. 返回群组列表（支持分页、搜索、筛选）
   ↓
8. 前端渲染群组卡片列表
```

**场景 C: 用户在 MiniApp 加入群组并领取进入奖励**

```
1. 用户在 MiniApp 中点击"加入群组"
   ↓
2. MiniApp 前端调用 POST /v1/groups/public/{group_id}/join (miniapp/main.py)
   ↓
3. MiniApp API 验证 JWT Token
   ↓
4. API 处理函数调用 public_group_service.join_group() (services/public_group_service.py)
   ↓
5. 服务层函数：
   - 检查用户是否已加入（去重）
   - 检查奖励池是否充足
   - 发放进入奖励（增加用户余额）
   - 扣减奖励池
   - 创建 PublicGroupMembership 记录
   - 写入 Ledger 流水
   - 记录事件 (public_group_tracking.record_event)
   ↓
6. 返回加入结果和奖励信息
   ↓
7. MiniApp 前端显示"已加入，获得 X 星奖励"
```

---

## 存储与外部依赖

### 数据库

**支持的数据库**:
- **开发环境**: SQLite（默认，`sqlite:///./data.sqlite`）
- **生产环境**: PostgreSQL 或 MySQL（推荐 PostgreSQL）

**主要数据表**（通过 SQLAlchemy ORM 模型定义）:

| 模型文件 | 表名 | 主要用途 |
|---------|------|----------|
| `models/user.py` | `users` | 用户信息（Telegram ID、余额、积分、语言等） |
| `models/envelope.py` | `envelopes` | 红包记录（金额、数量、状态、创建时间等） |
| `models/ledger.py` | `ledger` | 账本流水（所有余额变动的记录） |
| `models/recharge.py` | `recharge_orders` | 充值订单（订单状态、支付信息、金额等） |
| `models/public_group.py` | `public_groups` | 公开群组（群组信息、状态、风险评分等） |
| `models/public_group.py` | `public_group_activities` | 群组活动（活动信息、奖励、时间范围等） |
| `models/public_group.py` | `public_group_events` | 群组事件（用户浏览、点击、加入等事件记录） |
| `models/invite.py` | `invites` | 邀请关系（邀请人、被邀请人、奖励记录等） |
| `models/cover.py` | `covers` | 红包封面（封面图片、元数据等） |

**数据库初始化**: 通过 `models/db.py` 的 `init_db()` 函数自动创建所有表，支持轻量迁移（自动补齐缺失列）。

---

### 外部服务依赖

#### NowPayments 支付

**用途**: 处理加密货币充值（USDT、TON 等）

**相关文件**:
- `core/clients/nowpayments.py`: NowPayments API 客户端（创建订单、查询状态）
- `web_admin/controllers/ipn.py`: IPN 回调处理（接收支付结果，更新订单状态和用户余额）

**调用流程**:
1. 用户在前端创建充值订单
2. Web Admin 调用 NowPayments API 创建支付
3. NowPayments 回调 Web Admin 的 `/admin/ipn` 接口
4. IPN 处理函数验证签名，更新订单状态和用户余额

---

#### Google Sheet / Google Logger

**用途**: 
- **Google Sheet**: 同步用户数据到 Google Sheet（用于数据分析和导出）
- **Google Logger**: 记录日志到 Google（用于日志聚合和分析）

**相关文件**:
- `services/sheet_users.py`: Google Sheet 用户服务
- `services/google_logger.py`: Google 日志服务
- `web_admin/controllers/sheet_users.py`: Google Sheet 用户管理页面

**密钥文件**: `secrets/service_account.json`（Google Service Account 密钥）

**注意**: `secrets/` 目录不应提交到 Git，生产环境需要手动部署此文件。

---

#### OpenAI / OpenRouter

**用途**: AI 功能（生成活动文案、优化提示词等）

**相关文件**:
- `services/ai_service.py`: AI 服务（通用 AI 功能）
- `services/ai_activity_generator.py`: AI 活动生成器（生成活动文案、规则等）

**配置**: 通过环境变量 `OPENAI_API_KEY` 或 `OPENROUTER_API_KEY` 配置。

---

#### Telegram Bot API

**用途**: Bot 发送消息、创建群组、处理加入请求等

**调用方式**: 通过 aiogram 框架自动调用 Telegram Bot API。

---

### 敏感文件

**`secrets/service_account.json`**:
- Google Service Account 密钥文件
- 用于访问 Google Sheet API 和 Google Logger API
- **不应提交到 Git**（应在 `.gitignore` 中）
- 生产环境需要手动部署，文件权限应设置为 `600`

---

## 监控、日志与告警

### Prometheus 指标

**模块**: `monitoring/metrics.py`

**功能**: 提供 Prometheus 格式的监控指标

**暴露端点**: `GET /metrics` (Web Admin, 端口 8000)

**内置指标**:
- `app_uptime_seconds`: 应用运行时间（秒）
- `app_info`: 应用信息（应用名称、版本等）

**自定义指标**（通过 `monitoring/metrics.py` 的 `counter()` 和 `histogram()` 函数）:
- 可以定义业务指标（如请求数、响应时间、错误数等）
- 支持标签（label）用于多维度统计

**使用方式**: Prometheus 定期抓取 `/metrics` 端点，Grafana 可以基于这些指标创建仪表板。

---

### 日志系统

**应用日志**:
- 所有服务（Web Admin、MiniApp API、Telegram Bot）使用 Python `logging` 模块
- 日志输出到标准输出（stdout），可以通过 systemd/journalctl 或 Docker logs 查看

**关键日志点**:
- 红包发送失败: `services/hongbao_service.py` 中的错误日志
- 充值订单处理: `services/recharge_service.py` 和 `web_admin/controllers/ipn.py` 中的日志
- 公开群组创建: `services/public_group_service.py` 中的日志
- API 错误: `web_admin/controllers/*.py` 和 `miniapp/main.py` 中的错误日志

**审计日志**:
- 所有重要操作（余额调整、充值、红包发送等）记录到 `ledger` 表
- 通过 `web_admin/controllers/audit.py` 提供审计日志查询接口
- 支持按类型、用户、时间范围等条件筛选

---

### 告警机制

**健康检查**:
- `/healthz`: 基础健康检查（所有服务）
- `/readyz`: 就绪检查（Web Admin，检查数据库、静态目录等）

**监控指标**（参考 `docs/MONITORING_AND_ALERTING_CHECKLIST.md`）:
- 红包发送失败率
- 任务队列堆积
- 外部 API 调用错误数
- 响应时间 p95
- 充值订单失败率
- 数据库连接池使用率

**告警方式**: 可以通过 Prometheus Alertmanager 配置告警规则，发送到邮件、Slack、Telegram 等渠道。

---

## 部署视图

### 典型部署架构

在一台服务器上的典型部署方式：

```
┌─────────────────────────────────────────────────────────┐
│                    服务器（Server）                        │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │           反向代理（Nginx）                        │  │
│  │  - 处理 HTTPS、负载均衡、静态文件                    │  │
│  │  - 路由到后端服务（8000、8080、3001）                │  │
│  └──────────────────────────────────────────────────┘  │
│                          │                               │
│        ┌─────────────────┼─────────────────┐          │
│        │                 │                 │          │
│  ┌─────▼─────┐    ┌──────▼──────┐   ┌──────▼──────┐  │
│  │  Web      │    │  MiniApp    │   │  Frontend    │  │
│  │  Admin    │    │    API      │   │  (Next.js)   │  │
│  │  :8000    │    │   :8080     │   │   :3001      │  │
│  │ (Uvicorn) │    │ (Uvicorn)   │   │ (Node.js)    │  │
│  └─────┬─────┘    └──────┬──────┘   └──────────────┘  │
│        │                 │                            │
│        └─────────┬───────┘                            │
│                  │                                     │
│  ┌───────────────▼───────────────┐                    │
│  │      Database                 │                    │
│  │  (PostgreSQL / MySQL / SQLite)│                    │
│  └───────────────────────────────┘                    │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Telegram Bot (app.py)                     │  │
│  │  - 运行方式: systemd / supervisor / Docker         │  │
│  │  - 通过 aiogram 连接 Telegram Bot API             │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          │ HTTP
                          ▼
              ┌───────────────────────┐
              │  外部服务              │
              │  - Telegram Bot API    │
              │  - NowPayments API     │
              │  - OpenAI/OpenRouter   │
              │  - Google APIs         │
              └───────────────────────┘
```

### 服务通信方式

**内部通信**:
- **前端控制台 → Web Admin**: HTTP REST API (`http://localhost:8000/admin/api/v1/*`)
- **前端控制台 → MiniApp API**: HTTP REST API (`http://localhost:8080/v1/*`)
- **Telegram Bot → Web Admin**: HTTP REST API（内部调用，如创建红包任务）
- **所有服务 → 数据库**: SQLAlchemy ORM（直接数据库连接）

**外部通信**:
- **Web Admin → NowPayments**: HTTP REST API（创建订单、查询状态）
- **NowPayments → Web Admin**: HTTP POST（IPN 回调）
- **Web Admin → OpenAI/OpenRouter**: HTTP REST API（AI 功能）
- **Telegram Bot → Telegram Bot API**: HTTP REST API（通过 aiogram）
- **所有服务 → Google APIs**: HTTP REST API（Google Sheet、Google Logger）

### 部署方式

**开发环境**:
- 所有服务在同一台机器上运行
- 使用 SQLite 数据库（本地文件）
- 通过 `uvicorn --reload` 启动，支持热重载

**生产环境**:
- **数据库**: 独立 PostgreSQL/MySQL 服务器（或 Docker 容器）
- **Web Admin**: systemd 服务或 Docker 容器（Uvicorn/Gunicorn）
- **MiniApp API**: systemd 服务或 Docker 容器（Uvicorn）
- **前端控制台**: 
  - 方式 1: Next.js 服务器模式（`npm run start`）
  - 方式 2: 构建为静态文件（`npm run build`），通过 Nginx 提供
- **Telegram Bot**: systemd 服务或 Docker 容器（`python app.py`）
- **反向代理**: Nginx 处理 HTTPS、负载均衡、静态文件

**容器化部署**（可选）:
- 使用 Docker Compose 编排所有服务
- 每个服务一个容器（web-admin、miniapp-api、frontend、db、bot）
- 通过 Docker 网络通信

---

## 总结

037 红包系统管理后台采用**分层架构**和**多入口设计**：

- **分层清晰**: 数据模型层 → 业务服务层 → 控制器/路由层，职责分明，便于维护
- **多入口**: Telegram Bot、Web Admin、MiniApp API、前端控制台，满足不同使用场景
- **数据统一**: 所有服务共享同一数据库，通过服务层确保数据一致性
- **容错设计**: 前端实现 mock fallback，后端不可用时仍可展示数据
- **可扩展**: 支持多种数据库、外部服务集成、监控告警等

**快速上手建议**:
1. 先了解服务组件与端口（明确各服务的作用）
2. 理解后端分层结构（知道代码在哪里）
3. 熟悉典型数据流（理解请求如何流转）
4. 参考 `037_DEPLOY_GUIDE.md` 快速启动本地环境

---

*最后更新: 2025-01-XX*

