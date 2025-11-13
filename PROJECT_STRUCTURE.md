# 项目结构文档

本文档展示项目的完整目录结构，用于快速定位文件、排查端口配置和包名问题。

> **已排除的目录**: `.git`, `.idea`, `.vscode`, `node_modules`, `dist`, `build`, `.next`, `coverage`, `.venv`, `venv`, `env`, `__pycache__`, `.turbo`, `.cache` 以及所有隐藏文件

---

## 项目目录树

```
.
├─ app.py                          # Telegram Bot 主入口（aiogram）
├─ docker-compose.yml              # Docker Compose 配置文件
├─ Dockerfile                      # Docker 镜像构建文件
├─ Makefile                        # Make 命令定义
├─ pytest.ini                      # Pytest 测试配置
├─ requirements.txt                # Python 依赖列表
├─ start.sh                        # 启动脚本
├─ README.md                       # 项目主文档
├─ READMEV2.md                     # 项目文档 V2
├─ PROJECT_STRUCTURE.md            # 本文件（项目结构文档）
│
├─ web_admin/                      # FastAPI Web 管理后台（端口 8000）
│  ├─ main.py                      # FastAPI 应用入口
│  ├─ auth.py                      # 认证相关（登录、会话管理）
│  ├─ constants.py                 # 常量定义
│  ├─ deps.py                      # 依赖注入（数据库会话、认证等）
│  ├─ controllers/                 # 控制器（路由处理和业务逻辑）
│  │  ├─ dashboard.py              # Dashboard 页面和 API（统计数据）
│  │  ├─ envelopes.py              # 红包任务管理（任务列表、详情）
│  │  ├─ audit.py                  # 审计日志（操作记录）
│  │  ├─ logs.py                   # 系统日志 API
│  │  ├─ stats.py                  # 统计接口（趋势、概览、任务、群组统计）
│  │  ├─ settings.py               # 系统设置（金额限制、风控、通知）
│  │  ├─ users.py                  # 用户管理
│  │  ├─ public_groups.py          # 公开群组管理（列表、状态、活动）
│  │  ├─ public_group_reports.py   # 群组报告管理
│  │  ├─ recharge.py               # 充值订单管理
│  │  ├─ ledger.py                 # 账本管理
│  │  ├─ covers.py                 # 封面管理
│  │  ├─ invites.py                # 邀请管理
│  │  ├─ tags.py                   # 标签管理
│  │  ├─ export.py                 # 数据导出
│  │  ├─ queue.py                  # 导出任务队列
│  │  ├─ approvals.py              # 审批管理
│  │  ├─ adjust.py                 # 余额调整
│  │  ├─ reset.py                  # 重置操作
│  │  ├─ sheet_users.py            # Google Sheet 用户管理
│  │  ├─ ipn.py                    # NowPayments IPN 处理
│  │  ├─ a11y.py                   # 无障碍功能
│  │  └─ stats/                     # 统计相关子目录
│  └─ services/                     # Web Admin 服务层
│     └─ audit_service.py          # 审计服务
│
├─ frontend-next/                   # Next.js 前端控制台（端口 3001）
│  ├─ package.json                  # 项目依赖和脚本配置
│  ├─ package-lock.json             # 依赖锁定文件
│  ├─ next.config.ts                # Next.js 配置（端口、环境变量等）
│  ├─ tailwind.config.ts            # Tailwind CSS 配置
│  ├─ tsconfig.json                 # TypeScript 配置
│  ├─ components.json                # shadcn/ui 组件配置
│  ├─ postcss.config.mjs            # PostCSS 配置
│  ├─ eslint.config.mjs             # ESLint 配置
│  ├─ next-env.d.ts                 # Next.js 类型定义
│  ├─ README.md                     # 前端项目文档
│  ├─ public/                       # 静态资源目录
│  │  ├─ file.svg
│  │  ├─ globe.svg
│  │  ├─ next.svg
│  │  ├─ vercel.svg
│  │  └─ window.svg
│  └─ src/                          # 源代码目录
│     ├─ app/                       # Next.js App Router 页面目录
│     │  ├─ layout.tsx              # 根布局（全局导航、Providers）
│     │  ├─ providers.tsx           # 全局 Providers（React Query、Auth）
│     │  ├─ page.tsx                # Dashboard 首页 (/)
│     │  ├─ globals.css              # 全局样式
│     │  ├─ favicon.ico              # 网站图标
│     │  ├─ tasks/                   # 任务列表页
│     │  │  └─ page.tsx              # /tasks
│     │  ├─ groups/                  # 群组列表页
│     │  │  ├─ page.tsx              # /groups
│     │  │  └─ [id]/                 # 群组详情页
│     │  │     └─ page.tsx           # /groups/[id]
│     │  ├─ stats/                   # 红包统计页
│     │  │  └─ page.tsx              # /stats
│     │  ├─ logs/                    # 日志中心
│     │  │  ├─ page.tsx              # /logs
│     │  │  └─ audit/                # 审计日志
│     │  │     └─ page.tsx           # /logs/audit
│     │  ├─ settings/                # 系统设置页
│     │  │  └─ page.tsx              # /settings
│     │  └─ demo/                     # Demo 页面
│     │     └─ page.tsx              # /demo
│     ├─ api/                        # API 客户端目录
│     │  ├─ admin.ts                 # Web Admin API 客户端（端口 8000）
│     │  ├─ miniapp.ts               # MiniApp API 客户端（端口 8080）
│     │  ├─ http.ts                  # HTTP 客户端基础配置
│     │  ├─ health.ts                # 健康检查 API
│     │  ├─ auth.ts                  # 认证相关 API
│     │  └─ publicGroups.ts           # 公开群组 API
│     ├─ lib/                        # 工具库目录
│     │  ├─ api.ts                   # API 调用封装（含 mock fallback 逻辑）
│     │  └─ utils.ts                 # 工具函数
│     ├─ mock/                       # Mock 数据目录
│     │  ├─ dashboard.ts             # Dashboard mock 数据
│     │  ├─ groups.ts                # 群组列表 mock 数据
│     │  ├─ logs.ts                  # 日志 mock 数据
│     │  ├─ stats.ts                 # 统计 mock 数据
│     │  └─ user.ts                  # 用户信息 mock 数据
│     ├─ components/                # React 组件目录
│     │  ├─ layout/                  # 布局组件
│     │  │  └─ Navbar.tsx            # 导航栏组件
│     │  ├─ shared/                  # 共享业务组件
│     │  │  ├─ GroupCard.tsx         # 群组卡片组件
│     │  │  ├─ ActivityCard.tsx      # 活动卡片组件
│     │  │  ├─ ActivityDetailDialog.tsx  # 活动详情对话框
│     │  │  ├─ LoadingSkeleton.tsx   # 加载骨架屏
│     │  │  ├─ ErrorNotice.tsx        # 错误提示组件
│     │  │  └─ QueryDevtools.tsx     # React Query 开发工具
│     │  └─ ui/                      # shadcn/ui 基础组件
│     │     ├─ avatar.tsx            # 头像组件
│     │     ├─ badge.tsx             # 徽章组件
│     │     ├─ button.tsx            # 按钮组件
│     │     ├─ card.tsx              # 卡片组件
│     │     ├─ checkbox.tsx          # 复选框组件
│     │     ├─ dialog.tsx            # 对话框组件
│     │     ├─ dropdown-menu.tsx     # 下拉菜单组件
│     │     ├─ input.tsx             # 输入框组件
│     │     ├─ label.tsx             # 标签组件
│     │     ├─ navigation-menu.tsx    # 导航菜单组件
│     │     ├─ select.tsx            # 选择器组件
│     │     ├─ skeleton.tsx          # 骨架屏组件
│     │     ├─ table.tsx              # 表格组件
│     │     ├─ tabs.tsx               # 标签页组件
│     │     └─ textarea.tsx           # 文本域组件
│     ├─ hooks/                      # React Hooks 目录
│     │  ├─ usePublicGroups.ts       # 公开群组数据获取 Hook
│     │  └─ useTelegramWebApp.ts     # Telegram WebApp Hook
│     ├─ providers/                  # Context Providers 目录
│     │  └─ AuthProvider.tsx         # 认证状态管理 Provider
│     ├─ types/                      # TypeScript 类型定义目录
│     │  ├─ auth.ts                  # 认证相关类型
│     │  └─ publicGroups.ts          # 公开群组相关类型
│     └─ utils/                      # 工具函数目录
│        └─ telegram.ts             # Telegram WebApp 工具函数
│
├─ miniapp-frontend/                # Vite 前端（旧版，已弃用，仅作参考）
│  ├─ package.json
│  ├─ vite.config.ts                # Vite 配置
│  ├─ tailwind.config.js            # Tailwind CSS 配置
│  ├─ postcss.config.js             # PostCSS 配置
│  ├─ tsconfig.json                 # TypeScript 配置
│  ├─ index.html                    # HTML 入口
│  ├─ README.md
│  ├─ public/
│  │  └─ vite.svg
│  └─ src/
│     ├─ main.tsx                   # 入口文件
│     ├─ App.tsx                     # 主应用组件
│     ├─ index.css                   # 全局样式
│     ├─ env.d.ts                    # 环境变量类型定义
│     ├─ api/                        # API 客户端
│     ├─ components/                 # 组件
│     ├─ hooks/                      # Hooks
│     ├─ pages/                      # 页面组件
│     ├─ providers/                  # Providers
│     ├─ types/                      # 类型定义
│     └─ utils/                      # 工具函数
│
├─ miniapp/                         # MiniApp 后端 API（端口 8080）
│  ├─ main.py                       # FastAPI 应用入口
│  ├─ auth.py                       # 认证接口（Telegram 登录、密码登录）
│  ├─ security.py                   # JWT 安全（生成、验证、黑名单）
│  └─ middleware.py                 # 中间件（JWT 认证）
│
├─ models/                          # 数据模型（SQLAlchemy ORM）
│  ├─ db.py                         # 数据库连接和 Base 类
│  ├─ user.py                       # 用户模型
│  ├─ envelope.py                  # 红包模型
│  ├─ ledger.py                     # 账本模型（流水记录）
│  ├─ recharge.py                   # 充值订单模型
│  ├─ public_group.py               # 公开群组模型
│  ├─ invite.py                     # 邀请模型
│  └─ cover.py                      # 封面模型
│
├─ services/                        # 业务服务层
│  ├─ hongbao_service.py            # 红包服务（发送、领取）
│  ├─ recharge_service.py            # 充值服务（订单处理）
│  ├─ invite_service.py             # 邀请服务（邀请奖励）
│  ├─ export_service.py             # 导出服务（CSV、Excel）
│  ├─ public_group_service.py       # 公开群组服务（创建、管理）
│  ├─ public_group_activity.py      # 群组活动服务（活动管理）
│  ├─ public_group_report.py        # 群组报告服务（报告处理）
│  ├─ public_group_tracking.py      # 群组追踪服务（数据追踪）
│  ├─ ai_service.py                 # AI 服务（通用 AI 功能）
│  ├─ ai_helper.py                  # AI 辅助工具
│  ├─ ai_activity_generator.py     # AI 活动生成器
│  ├─ google_logger.py              # Google 日志服务
│  ├─ sheet_users.py                # Google Sheet 用户服务
│  └─ safe_send.py                  # 安全发送服务
│
├─ routers/                         # Telegram Bot 路由（aiogram handlers）
│  ├─ __init__.py
│  ├─ hongbao.py                    # 红包相关命令
│  ├─ envelope.py                   # 红包操作
│  ├─ recharge.py                   # 充值相关
│  ├─ withdraw.py                   # 提现相关
│  ├─ balance.py                    # 余额查询
│  ├─ invite.py                     # 邀请相关
│  ├─ admin.py                      # 管理员命令
│  ├─ admin_adjust.py               # 管理员调整
│  ├─ admin_covers.py               # 管理员封面
│  ├─ public_group.py               # 公开群组
│  ├─ menu.py                       # 菜单
│  ├─ welcome.py                    # 欢迎消息
│  ├─ help.py                       # 帮助命令
│  ├─ today.py                      # 今日统计
│  ├─ rank.py                       # 排行榜
│  ├─ welfare.py                    # 福利
│  ├─ member.py                     # 成员相关
│  └─ nowp_ipn.py                   # NowPayments IPN
│
├─ core/                            # 核心功能模块
│  ├─ i18n/                         # 国际化模块
│  │  ├─ i18n.py                    # i18n 核心（翻译加载、获取）
│  │  └─ messages/                 # 翻译文件目录
│  │     ├─ zh.yml                  # 中文翻译
│  │     ├─ en.yml                  # 英文翻译
│  │     ├─ de.yml                  # 德语翻译
│  │     ├─ es.yml                  # 西班牙语翻译
│  │     ├─ fil.yml                 # 菲律宾语翻译
│  │     ├─ fr.yml                  # 法语翻译
│  │     ├─ hi.yml                  # 印地语翻译
│  │     ├─ id.yml                  # 印尼语翻译
│  │     ├─ ms.yml                  # 马来语翻译
│  │     ├─ pt.yml                  # 葡萄牙语翻译
│  │     ├─ th.yml                  # 泰语翻译
│  │     └─ vi.yml                  # 越南语翻译
│  ├─ middlewares/                  # 中间件模块
│  │  ├─ errors.py                  # 错误处理中间件
│  │  ├─ throttling.py              # 限流中间件
│  │  ├─ user_bootstrap.py          # 用户引导中间件
│  │  └─ anti_echo.py               # 防回显中间件
│  ├─ clients/                      # 外部客户端
│  │  └─ nowpayments.py             # NowPayments 支付客户端
│  └─ utils/                        # 工具函数
│     └─ keyboards.py               # 键盘工具（Inline Keyboard）
│
├─ config/                          # 配置模块
│  ├─ settings.py                   # 全局配置（环境变量读取）
│  ├─ feature_flags.py              # 功能开关配置
│  └─ load_env.py                   # 环境变量加载
│
├─ templates/                       # HTML 模板（Jinja2，用于 Web Admin）
│  ├─ base.html                     # 基础模板
│  ├─ login.html                    # 登录页
│  ├─ dashboard.html                # Dashboard 页
│  ├─ public_groups.html            # 公开群组页
│  ├─ public_groups_dashboard.html  # 群组 Dashboard
│  ├─ public_groups_activities.html # 群组活动
│  ├─ public_groups_reports.html    # 群组报告
│  ├─ users_list.html               # 用户列表
│  ├─ ledger.html                   # 账本页
│  ├─ audit.html                    # 审计日志页
│  ├─ recharge_orders.html          # 充值订单页
│  ├─ settings.html                 # 设置页
│  ├─ covers_list.html              # 封面列表
│  ├─ invites.html                  # 邀请列表
│  ├─ tags.html                     # 标签管理
│  └─ _macros/                      # 模板宏
│     └─ icons.html                 # 图标宏
│
├─ static/                          # 静态文件目录
│  └─ uploads/                      # 上传文件目录
│
├─ scripts/                         # 脚本工具目录
│  ├─ seed_public_groups.py         # 初始化公开群组数据
│  ├─ self_check.py                 # 自检脚本（健康检查、测试）
│  ├─ check_env.py                  # 环境检查脚本
│  ├─ cleanup_db.py                 # 数据库清理脚本
│  ├─ load_test_users.py            # 加载测试用户
│  ├─ export_translations.py        # 导出翻译脚本
│  ├─ import_translations.py        # 导入翻译脚本
│  ├─ activity_report_cron.py       # 活动报告定时任务
│  ├─ demo_flow.py                  # 演示流程脚本
│  └─ manifest.py                   # 清单生成脚本
│
├─ tests/                           # 测试文件目录
│  ├─ test_models.py                # 模型测试
│  ├─ test_services.py              # 服务测试
│  ├─ test_miniapp_auth.py          # MiniApp 认证测试
│  ├─ test_api_public_groups.py     # 公开群组 API 测试
│  ├─ test_public_group_service.py  # 群组服务测试
│  ├─ test_public_group_reports.py  # 群组报告测试
│  ├─ test_ai_activity_generator.py # AI 生成器测试
│  ├─ test_activity_report_cron.py  # 活动报告定时任务测试
│  ├─ test_activity_webhooks.py     # 活动 Webhook 测试
│  ├─ test_web_admin_public_groups.py  # Web Admin 公开群组测试
│  ├─ test_i18n.py                  # 国际化测试
│  ├─ test_end_to_end.py            # 端到端测试
│  └─ test_regression_features.py   # 回归测试
│
├─ docs/                            # 项目文档目录
│  ├─ PORTS_AND_SERVICES.md         # 端口和服务说明
│  ├─ DASHBOARD_API.md              # Dashboard API 文档
│  ├─ DASHBOARD_IMPLEMENTATION_SUMMARY.md  # Dashboard 实现总结
│  ├─ public_group_ops.md           # 公开群组操作文档
│  ├─ i18n_translation_plan.md      # i18n 翻译计划
│  ├─ branding_guidelines.md         # 品牌指南
│  └─ T6_summary.md                 # T6 总结
│
├─ assets/                          # 资源文件目录
│  ├─ cover.jpg                     # 封面图片
│  ├─ cover_zh.jpg                  # 中文封面
│  ├─ cover_en.jpg                  # 英文封面
│  └─ 封面图片说明.txt               # 封面说明
│
├─ exports/                         # 导出文件目录（运行时生成）
│  └─ *.xlsx                        # Excel 导出文件
│
├─ secrets/                         # 密钥文件目录（不应提交到 Git）
│  └─ service_account.json          # Google Service Account 密钥
│
├─ monitoring/                      # 监控模块
│  └─ metrics.py                    # Prometheus 指标
│
├─ middlewares/                     # 全局中间件
│  └─ profile_sync.py               # 用户资料同步中间件
│
├─ locales/                         # 本地化字符串
│  └─ strings.py                    # 字符串定义
│
├─ saas-demo/                       # SaaS Demo 项目（Next.js 模板，参考用）
│  ├─ package.json
│  ├─ components.json
│  ├─ next.config.ts
│  ├─ tailwind.config.ts
│  ├─ tsconfig.json
│  ├─ src/
│  └─ ...
│
└─ *.sqlite                         # SQLite 数据库文件（运行时生成）
   ├─ data.sqlite                  # 主数据库
   ├─ runtime.sqlite                # 运行时数据库
   └─ test_*.sqlite                 # 测试数据库
```

---

## Next.js 前端页面入口文件列表

所有页面文件位于 `frontend-next/src/app/` 目录下：

| 路径 | 文件 | 路由 | 说明 |
|------|------|------|------|
| `/` | `page.tsx` | `/` | Dashboard 首页（统计卡片、趋势图、任务列表） |
| `/tasks` | `tasks/page.tsx` | `/tasks` | 任务列表页（红包发送任务） |
| `/groups` | `groups/page.tsx` | `/groups` | 群组列表页（公开群组） |
| `/groups/[id]` | `groups/[id]/page.tsx` | `/groups/:id` | 群组详情页（动态路由） |
| `/stats` | `stats/page.tsx` | `/stats` | 红包统计页（统计图表） |
| `/logs` | `logs/page.tsx` | `/logs` | 日志中心（系统日志） |
| `/logs/audit` | `logs/audit/page.tsx` | `/logs/audit` | 审计日志页（操作记录） |
| `/settings` | `settings/page.tsx` | `/settings` | 系统设置页（金额限制、风控、通知） |
| `/demo` | `demo/page.tsx` | `/demo` | Demo 页面（组件展示） |

**布局文件**:
- `layout.tsx` - 根布局（全局导航、Providers 包装）
- `providers.tsx` - 全局 Providers（React Query、Auth）

---

## API 客户端位置

### 主要 API 封装

| 文件 | 路径 | 说明 |
|------|------|------|
| `api.ts` | `frontend-next/src/lib/api.ts` | **主要 API 封装**，包含所有业务 API 调用和 mock fallback 逻辑 |
| `admin.ts` | `frontend-next/src/api/admin.ts` | Web Admin API 客户端（端口 8000，Axios 实例） |
| `miniapp.ts` | `frontend-next/src/api/miniapp.ts` | MiniApp API 客户端（端口 8080，Axios 实例） |
| `http.ts` | `frontend-next/src/api/http.ts` | HTTP 客户端基础配置 |
| `health.ts` | `frontend-next/src/api/health.ts` | 健康检查 API |
| `auth.ts` | `frontend-next/src/api/auth.ts` | 认证相关 API |
| `publicGroups.ts` | `frontend-next/src/api/publicGroups.ts` | 公开群组 API |

### API 调用函数（在 `lib/api.ts` 中）

- `getDashboard()` - 获取 Dashboard 数据（含趋势统计）
- `getTasks()` - 获取任务列表
- `getTaskDetail()` - 获取任务详情
- `getGroupList()` - 获取群组列表
- `getLogs()` - 获取系统日志
- `getAuditLogs()` - 获取审计日志
- `getRedPacketStats()` - 获取红包统计
- `getSettings()` - 获取系统设置
- `updateSettings()` - 更新系统设置
- `getStatsTrends()` - 获取趋势统计

所有 API 调用都包含 **mock fallback 机制**，接口失败时自动使用 mock 数据。

---

## Mock 数据目录

Mock 数据位于 `frontend-next/src/mock/` 目录：

| 文件 | 说明 | 使用场景 |
|------|------|----------|
| `dashboard.ts` | Dashboard mock 数据（统计卡片、趋势图、任务列表） | Dashboard 页面接口失败时使用 |
| `groups.ts` | 群组列表 mock 数据 | 群组列表页接口失败时使用 |
| `logs.ts` | 日志 mock 数据（系统日志、审计日志） | 日志页面接口失败时使用 |
| `stats.ts` | 红包统计 mock 数据 | 统计页面接口失败时使用 |
| `user.ts` | 用户信息 mock 数据 | 用户信息接口失败时使用 |

**Mock Fallback 机制**:
- 所有 API 调用在 `lib/api.ts` 中使用 `apiCallWithMock()` 函数
- 当接口返回 404/500 或网络错误时，自动使用对应的 mock 数据
- Dashboard 页面使用 mock 数据时会显示黄色提示条

---

## Hooks 目录说明

Hooks 位于 `frontend-next/src/hooks/` 目录：

| 文件 | 说明 | 用途 |
|------|------|------|
| `usePublicGroups.ts` | 公开群组数据获取 Hook | 使用 React Query 获取群组列表、活动列表、详情等 |
| `useTelegramWebApp.ts` | Telegram WebApp Hook | 管理 Telegram WebApp 状态、主题、参数等 |

**Hook 特点**:
- 基于 React Query，提供自动缓存、重试、刷新功能
- 统一的错误处理和加载状态管理
- 支持自动刷新（refetchInterval）

---

## 组件目录说明

组件位于 `frontend-next/src/components/` 目录：

### 布局组件 (`layout/`)

| 文件 | 说明 |
|------|------|
| `Navbar.tsx` | 全局导航栏（Dashboard、任务列表、群组、统计、日志、设置） |

### 共享业务组件 (`shared/`)

| 文件 | 说明 |
|------|------|
| `GroupCard.tsx` | 群组卡片组件（显示群组信息、标签、状态） |
| `ActivityCard.tsx` | 活动卡片组件（显示活动信息、奖励、时间） |
| `ActivityDetailDialog.tsx` | 活动详情对话框（查看详情、参与活动） |
| `LoadingSkeleton.tsx` | 加载骨架屏组件（数据加载时显示） |
| `ErrorNotice.tsx` | 错误提示组件（显示错误信息、重试按钮） |
| `QueryDevtools.tsx` | React Query 开发工具（开发环境调试用） |

### UI 基础组件 (`ui/`)

shadcn/ui 组件库的基础组件：

| 文件 | 说明 |
|------|------|
| `card.tsx` | 卡片组件 |
| `button.tsx` | 按钮组件 |
| `badge.tsx` | 徽章组件 |
| `table.tsx` | 表格组件 |
| `dialog.tsx` | 对话框组件 |
| `input.tsx` | 输入框组件 |
| `select.tsx` | 选择器组件 |
| `tabs.tsx` | 标签页组件 |
| `skeleton.tsx` | 骨架屏组件 |
| `avatar.tsx` | 头像组件 |
| `checkbox.tsx` | 复选框组件 |
| `dropdown-menu.tsx` | 下拉菜单组件 |
| `label.tsx` | 标签组件 |
| `navigation-menu.tsx` | 导航菜单组件 |
| `textarea.tsx` | 文本域组件 |

---

## 配置文件列表

### Next.js 前端配置

| 文件 | 说明 |
|------|------|
| `package.json` | 项目依赖和脚本（dev、build、start） |
| `next.config.ts` | Next.js 配置（端口、环境变量、构建选项） |
| `tailwind.config.ts` | Tailwind CSS 配置（主题、颜色、插件） |
| `tsconfig.json` | TypeScript 配置（路径别名、编译选项） |
| `components.json` | shadcn/ui 组件配置 |
| `postcss.config.mjs` | PostCSS 配置（Tailwind 插件） |
| `eslint.config.mjs` | ESLint 配置（代码检查规则） |

### 后端配置

| 文件 | 说明 |
|------|------|
| `requirements.txt` | Python 依赖列表 |
| `pytest.ini` | Pytest 测试配置 |
| `docker-compose.yml` | Docker Compose 配置 |
| `Dockerfile` | Docker 镜像构建配置 |
| `Makefile` | Make 命令定义 |
| `start.sh` | 启动脚本 |

### 环境配置

| 文件 | 说明 |
|------|------|
| `config/settings.py` | 全局配置（从环境变量读取） |
| `config/feature_flags.py` | 功能开关配置 |
| `config/load_env.py` | 环境变量加载 |

---

## 端口和服务映射

| 端口 | 服务 | 入口文件 | 说明 |
|------|------|----------|------|
| **8000** | FastAPI Web Admin | `web_admin/main.py` | Web 管理后台（HTML 页面 + REST API） |
| **8080** | FastAPI MiniApp API | `miniapp/main.py` | MiniApp 后端 API（Telegram WebApp） |
| **3001** | Next.js 前端控制台 | `frontend-next/` | 红包系统控制台（Next.js + Tailwind） |
| **3000** | Next.js 聊天 AI 控制台 | `saas-demo/` | 聊天 AI 控制台（独立项目） |

---

## API 路径前缀

| 前缀 | 服务 | 说明 |
|------|------|------|
| `/admin/api/v1/` | Web Admin REST API | 管理后台 API（端口 8000） |
| `/v1/` | MiniApp REST API | MiniApp API（端口 8080） |
| `/healthz` | 健康检查 | 所有服务通用 |

---

## 快速定位指南

### 查找后端接口

- **Dashboard API**: `web_admin/controllers/dashboard.py`
- **任务列表 API**: `web_admin/controllers/envelopes.py`
- **统计 API**: `web_admin/controllers/stats.py`
- **日志 API**: `web_admin/controllers/logs.py`
- **审计日志 API**: `web_admin/controllers/audit.py`
- **群组列表 API**: `web_admin/controllers/public_groups.py` (api_router)

### 查找前端页面

- **Dashboard**: `frontend-next/src/app/page.tsx`
- **任务列表**: `frontend-next/src/app/tasks/page.tsx`
- **群组列表**: `frontend-next/src/app/groups/page.tsx`
- **群组详情**: `frontend-next/src/app/groups/[id]/page.tsx`
- **统计页面**: `frontend-next/src/app/stats/page.tsx`
- **日志中心**: `frontend-next/src/app/logs/page.tsx`
- **审计日志**: `frontend-next/src/app/logs/audit/page.tsx`
- **系统设置**: `frontend-next/src/app/settings/page.tsx`

### 查找 API 客户端

- **主要 API 封装**: `frontend-next/src/lib/api.ts`
- **Web Admin API 客户端**: `frontend-next/src/api/admin.ts`
- **MiniApp API 客户端**: `frontend-next/src/api/miniapp.ts`

### 查找 Mock 数据

- **Dashboard Mock**: `frontend-next/src/mock/dashboard.ts`
- **群组 Mock**: `frontend-next/src/mock/groups.ts`
- **日志 Mock**: `frontend-next/src/mock/logs.ts`
- **统计 Mock**: `frontend-next/src/mock/stats.ts`
- **用户 Mock**: `frontend-next/src/mock/user.ts`

---

## 启动命令

### 后端服务

```bash
# Web Admin (端口 8000)
uvicorn web_admin.main:app --host 0.0.0.0 --port 8000 --reload

# MiniApp API (端口 8080)
uvicorn miniapp.main:app --host 0.0.0.0 --port 8080 --reload

# Telegram Bot
python app.py
```

### 前端服务

```bash
# Next.js 前端控制台 (端口 3001)
cd frontend-next
npm install
npm run dev

# Vite 前端 (旧版，已弃用)
cd miniapp-frontend
npm install
npm run dev
```

---

## 注意事项

1. **端口冲突**: 确保 8000、8080、3001 端口未被占用
2. **数据库文件**: `*.sqlite` 文件是运行时生成的，不应提交到 Git
3. **环境变量**: 配置在 `config/settings.py` 中读取，通过 `.env` 文件设置
4. **Mock 数据**: 前端在接口失败时自动使用 mock 数据，确保开发体验
5. **API 文档**: FastAPI 自动生成文档，访问 `http://localhost:8000/docs`（如果启用）
6. **启动顺序**: 建议先启动后端服务（8000），再启动前端服务（3001）

---

*最后更新: 2025-01-XX*
