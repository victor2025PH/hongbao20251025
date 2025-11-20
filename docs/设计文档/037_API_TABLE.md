# API 对照表

本文档列出所有 FastAPI 后端接口，按模块分类，便于快速查阅。

> **说明**: 本文档基于 `web_admin/main.py` 和 `miniapp/main.py` 的实际代码生成。如有遗漏或变更，请及时更新。

---

## 目录

- [Web Admin API (端口 8000)](#web-admin-api-端口-8000)
- [MiniApp API (端口 8080)](#miniapp-api-端口-8080)
- [鉴权说明](#鉴权说明)

---

## Web Admin API (端口 8000)

### 健康检查

| 方法 | 路径 | 控制器文件 | 主要用途 | 鉴权 |
|------|------|------------|----------|------|
| GET | `/healthz` | `web_admin/main.py` | 基础健康检查 | 无 |
| GET | `/readyz` | `web_admin/main.py` | 就绪检查（数据库、静态目录等） | 无 |
| GET | `/metrics` | `web_admin/main.py` | Prometheus 指标 | 无 |

---

### Dashboard / 统计

| 方法 | 路径 | 控制器文件 | 主要用途 | 鉴权 |
|------|------|------------|----------|------|
| GET | `/admin/dashboard` | `web_admin/controllers/dashboard.py` | Dashboard HTML 页面 | 需登录 |
| GET | `/admin/api/v1/dashboard` | `web_admin/controllers/dashboard.py` | Dashboard 统计数据（JSON） | 需登录 |
| GET | `/admin/api/v1/dashboard/public` | `web_admin/controllers/dashboard.py` | Dashboard 统计数据（公开，带 mock fallback） | 无 |
| GET | `/admin/api/v1/dashboard/stats` | `web_admin/controllers/dashboard.py` | Dashboard 统计数据（旧版接口） | 需登录 |
| GET | `/admin/api/v1/dashboard/stats/public` | `web_admin/controllers/dashboard.py` | Dashboard 统计数据（公开，旧版接口） | 无 |
| GET | `/admin/api/v1/stats` | `web_admin/controllers/stats.py` | 趋势统计（最近 N 天） | 需登录 |
| GET | `/admin/api/v1/stats/overview` | `web_admin/controllers/stats.py` | 整体概览统计 | 需登录 |
| GET | `/admin/api/v1/stats/tasks` | `web_admin/controllers/stats.py` | 任务维度统计 | 需登录 |
| GET | `/admin/api/v1/stats/groups` | `web_admin/controllers/stats.py` | 群组维度统计 | 需登录 |

---

### 红包 / 任务

| 方法 | 路径 | 控制器文件 | 主要用途 | 鉴权 |
|------|------|------------|----------|------|
| GET | `/admin/envelopes/{eid}` | `web_admin/controllers/envelopes.py` | 红包详情 HTML 页面 | 需登录 |
| GET | `/admin/api/v1/tasks` | `web_admin/controllers/envelopes.py` | 任务列表（分页、搜索、筛选） | 需登录 |
| GET | `/admin/api/v1/tasks/{task_id}` | `web_admin/controllers/envelopes.py` | 任务详情（包含领取记录） | 需登录 |

---

### 充值订单

| 方法 | 路径 | 控制器文件 | 主要用途 | 鉴权 |
|------|------|------------|----------|------|
| GET | `/admin/recharge` | `web_admin/controllers/recharge.py` | 充值订单列表 HTML 页面 | 需登录 |
| POST | `/admin/recharge/refresh` | `web_admin/controllers/recharge.py` | 刷新订单状态 | 需登录 |
| POST | `/admin/recharge/expire` | `web_admin/controllers/recharge.py` | 标记订单为过期 | 需登录 |
| POST | `/admin/ipn` | `web_admin/controllers/ipn.py` | NowPayments IPN 回调 | 无（IPN 签名验证） |
| GET | `/admin/ipn/health` | `web_admin/controllers/ipn.py` | IPN 健康检查 | 无 |

---

### 账本 / 审计日志

| 方法 | 路径 | 控制器文件 | 主要用途 | 鉴权 |
|------|------|------------|----------|------|
| GET | `/admin/ledger` | `web_admin/controllers/ledger.py` | 账本列表 HTML 页面 | 需登录 |
| GET | `/admin/ledger/export.csv` | `web_admin/controllers/ledger.py` | 导出账本（CSV） | 需登录 |
| GET | `/admin/ledger/export.json` | `web_admin/controllers/ledger.py` | 导出账本（JSON） | 需登录 |
| GET | `/admin/audit` | `web_admin/controllers/audit.py` | 审计日志 HTML 页面 | 需登录 |
| GET | `/admin/api/v1/audit` | `web_admin/controllers/audit.py` | 审计日志列表（JSON，分页、筛选） | 需登录 |
| GET | `/admin/audit/export.csv` | `web_admin/controllers/audit.py` | 导出审计日志（CSV） | 需登录 |
| GET | `/admin/audit/export.json` | `web_admin/controllers/audit.py` | 导出审计日志（JSON） | 需登录 |

---

### 系统日志

| 方法 | 路径 | 控制器文件 | 主要用途 | 鉴权 |
|------|------|------------|----------|------|
| GET | `/admin/api/v1/logs` | `web_admin/controllers/logs.py` | 系统日志列表（JSON，分页、筛选） | 需登录 |
| GET | `/admin/api/v1/logs/audit` | `web_admin/controllers/logs.py` | 审计日志列表（JSON，分页、筛选） | 需登录 |

---

### 公开群组

| 方法 | 路径 | 控制器文件 | 主要用途 | 鉴权 |
|------|------|------------|----------|------|
| GET | `/admin/public-groups` | `web_admin/controllers/public_groups.py` | 公开群组列表 HTML 页面 | 需登录 |
| GET | `/admin/public-groups/dashboard` | `web_admin/controllers/public_groups.py` | 公开群组 Dashboard HTML 页面 | 需登录 |
| GET | `/admin/public-groups/activities` | `web_admin/controllers/public_groups.py` | 活动列表 HTML 页面 | 需登录 |
| POST | `/admin/public-groups/activities` | `web_admin/controllers/public_groups.py` | 创建活动 | 需登录 |
| POST | `/admin/public-groups/status/{group_id}` | `web_admin/controllers/public_groups.py` | 更新群组状态 | 需登录 |
| POST | `/admin/public-groups/bulk/status` | `web_admin/controllers/public_groups.py` | 批量更新群组状态 | 需登录 |
| POST | `/admin/public-groups/activities/bulk` | `web_admin/controllers/public_groups.py` | 批量更新活动 | 需登录 |
| POST | `/admin/public-groups/activities/ai-draft` | `web_admin/controllers/public_groups.py` | AI 生成活动草稿 | 需登录 |
| GET | `/admin/public-groups/activities/ai-history` | `web_admin/controllers/public_groups.py` | AI 生成历史 | 需登录 |
| POST | `/admin/public-groups/activities/ai-history/{history_id}/reapply` | `web_admin/controllers/public_groups.py` | 重新应用 AI 生成的活动 | 需登录 |
| GET | `/admin/public-groups/stats` | `web_admin/controllers/public_groups.py` | 群组统计数据 | 需登录 |
| GET | `/admin/public-groups/activities/insights` | `web_admin/controllers/public_groups.py` | 活动洞察 HTML 页面 | 需登录 |
| GET | `/admin/public-groups/activities/insights/data` | `web_admin/controllers/public_groups.py` | 活动洞察数据（JSON） | 需登录 |
| GET | `/admin/public-groups/activities/export` | `web_admin/controllers/public_groups.py` | 导出活动数据 | 需登录 |
| POST | `/admin/public-groups/activities/{activity_id}/toggle` | `web_admin/controllers/public_groups.py` | 切换活动状态 | 需登录 |
| GET | `/admin/public-groups/activities/report` | `web_admin/controllers/public_groups.py` | 活动报告 HTML 页面 | 需登录 |
| GET | `/admin/api/v1/group-list` | `web_admin/controllers/public_groups.py` | 群组列表（JSON，分页、搜索、筛选） | 需登录 |

---

### 用户管理

| 方法 | 路径 | 控制器文件 | 主要用途 | 鉴权 |
|------|------|------------|----------|------|
| GET | `/admin/users` | `web_admin/controllers/users.py` | 用户列表 HTML 页面 | 需登录（管理员） |
| GET | `/admin/users/{user_ref}` | `web_admin/controllers/users.py` | 用户详情 HTML 页面 | 需登录（管理员） |
| GET | `/admin/users/export.csv` | `web_admin/controllers/users.py` | 导出用户（CSV） | 需登录（管理员） |
| GET | `/admin/users/export.json` | `web_admin/controllers/users.py` | 导出用户（JSON） | 需登录（管理员） |

---

### 系统设置

| 方法 | 路径 | 控制器文件 | 主要用途 | 鉴权 |
|------|------|------------|----------|------|
| GET | `/admin/settings` | `web_admin/controllers/settings.py` | 系统设置 HTML 页面 | 需登录 |
| POST | `/admin/settings/toggle` | `web_admin/controllers/settings.py` | 切换功能开关 | 需登录 |
| GET | `/admin/api/v1/settings` | `web_admin/controllers/settings.py` | 获取系统设置（JSON） | 需登录 |
| PUT | `/admin/api/v1/settings` | `web_admin/controllers/settings.py` | 更新系统设置（JSON） | 需登录 |

---

### 其他管理功能

| 方法 | 路径 | 控制器文件 | 主要用途 | 鉴权 |
|------|------|------------|----------|------|
| GET | `/admin/covers` | `web_admin/controllers/covers.py` | 封面列表 HTML 页面 | 需登录 |
| POST | `/admin/covers/upload` | `web_admin/controllers/covers.py` | 上传封面 | 需登录 |
| POST | `/admin/covers/{cover_id}/toggle` | `web_admin/controllers/covers.py` | 切换封面状态 | 需登录 |
| POST | `/admin/covers/{cover_id}/delete` | `web_admin/controllers/covers.py` | 删除封面 | 需登录 |
| GET | `/admin/invites` | `web_admin/controllers/invites.py` | 邀请列表 HTML 页面 | 需登录 |
| GET | `/admin/invites/top` | `web_admin/controllers/invites.py` | 邀请排行榜 HTML 页面 | 需登录 |
| GET | `/admin/approvals` | `web_admin/controllers/approvals.py` | 审批列表 HTML 页面 | 需登录 |
| POST | `/admin/approvals/enqueue` | `web_admin/controllers/approvals.py` | 入队审批任务 | 需登录 |
| POST | `/admin/approvals/{aid}/approve` | `web_admin/controllers/approvals.py` | 批准审批 | 需登录 |
| POST | `/admin/approvals/{aid}/reject` | `web_admin/controllers/approvals.py` | 拒绝审批 | 需登录 |
| GET | `/admin/queue` | `web_admin/controllers/queue.py` | 任务队列 HTML 页面 | 需登录 |
| POST | `/admin/queue/enqueue` | `web_admin/controllers/queue.py` | 入队任务 | 需登录 |
| GET | `/admin/queue/status` | `web_admin/controllers/queue.py` | 队列状态 | 需登录 |
| GET | `/admin/queue/download/{job_id}` | `web_admin/controllers/queue.py` | 下载任务结果 | 需登录 |
| GET | `/admin/export` | `web_admin/controllers/export.py` | 导出页面 HTML | 需登录 |
| POST | `/admin/export/all` | `web_admin/controllers/export.py` | 导出所有数据 | 需登录 |
| POST | `/admin/export/users` | `web_admin/controllers/export.py` | 导出用户数据 | 需登录 |
| GET | `/admin/adjust` | `web_admin/controllers/adjust.py` | 余额调整 HTML 页面 | 需登录（管理员） |
| POST | `/admin/adjust/preview` | `web_admin/controllers/adjust.py` | 预览余额调整 | 需登录（管理员） |
| POST | `/admin/adjust/do` | `web_admin/controllers/adjust.py` | 执行余额调整 | 需登录（管理员） |
| GET | `/admin/reset` | `web_admin/controllers/reset.py` | 重置页面 HTML | 需登录（管理员） |
| POST | `/admin/reset/preview` | `web_admin/controllers/reset.py` | 预览重置 | 需登录（管理员） |
| POST | `/admin/reset/preview_all` | `web_admin/controllers/reset.py` | 预览全部重置 | 需登录（管理员） |
| POST | `/admin/reset/do_selected` | `web_admin/controllers/reset.py` | 执行选中重置 | 需登录（管理员） |
| POST | `/admin/reset/do_all` | `web_admin/controllers/reset.py` | 执行全部重置 | 需登录（管理员） |
| GET | `/admin/sheet-users` | `web_admin/controllers/sheet_users.py` | Google Sheet 用户列表 HTML 页面 | 需登录 |
| GET | `/admin/sheet-users/edit` | `web_admin/controllers/sheet_users.py` | 编辑用户页面 | 需登录 |
| POST | `/admin/sheet-users/edit` | `web_admin/controllers/sheet_users.py` | 保存用户编辑 | 需登录 |
| POST | `/admin/sheet-users/inline` | `web_admin/controllers/sheet_users.py` | 内联编辑用户 | 需登录 |
| GET | `/admin/sheet-users/export` | `web_admin/controllers/sheet_users.py` | 导出用户 | 需登录 |
| GET | `/admin/sheet-users/export-audit` | `web_admin/controllers/sheet_users.py` | 导出审计日志 | 需登录 |
| GET | `/admin/tags` | `web_admin/controllers/tags.py` | 标签管理 HTML 页面 | 需登录 |
| POST | `/admin/tags/disable` | `web_admin/controllers/tags.py` | 禁用标签 | 需登录 |
| POST | `/admin/tags/enable` | `web_admin/controllers/tags.py` | 启用标签 | 需登录 |
| GET | `/admin/public-groups/reports` | `web_admin/controllers/public_group_reports.py` | 群组报告列表 HTML 页面 | 需登录 |
| GET | `/admin/public-groups/reports/{report_id}` | `web_admin/controllers/public_group_reports.py` | 群组报告详情 HTML 页面 | 需登录 |
| POST | `/admin/public-groups/reports/{report_id}/resolve` | `web_admin/controllers/public_group_reports.py` | 解决报告 | 需登录 |
| POST | `/admin/public-groups/reports/{report_id}/dismiss` | `web_admin/controllers/public_group_reports.py` | 驳回报告 | 需登录 |
| POST | `/admin/public-groups/reports/{report_id}/escalate` | `web_admin/controllers/public_group_reports.py` | 升级报告 | 需登录 |
| GET | `/admin/a11y` | `web_admin/controllers/a11y.py` | 无障碍功能 HTML 页面 | 需登录 |
| GET | `/admin/a11y/json` | `web_admin/controllers/a11y.py` | 无障碍功能 JSON 数据 | 需登录 |

---

### 认证相关

| 方法 | 路径 | 控制器文件 | 主要用途 | 鉴权 |
|------|------|------------|----------|------|
| GET | `/admin/login` | `web_admin/auth.py` | 登录页面 | 无 |
| POST | `/admin/login` | `web_admin/auth.py` | 处理登录 | 无 |
| GET | `/admin/logout` | `web_admin/auth.py` | 登出 | 无 |
| GET | `/admin/twofactor` | `web_admin/auth.py` | 二次验证页面 | 无 |
| POST | `/admin/twofactor` | `web_admin/auth.py` | 处理二次验证 | 无 |

---

## MiniApp API (端口 8080)

### 健康检查

| 方法 | 路径 | 控制器文件 | 主要用途 | 鉴权 |
|------|------|------------|----------|------|
| GET | `/healthz` | `miniapp/main.py` | 基础健康检查 | 无 |

---

### 认证

| 方法 | 路径 | 控制器文件 | 主要用途 | 鉴权 |
|------|------|------------|----------|------|
| POST | `/api/auth/login` | `miniapp/auth.py` | 用户登录（Telegram code 或密码） | 无 |

---

### 公开群组

| 方法 | 路径 | 控制器文件 | 主要用途 | 鉴权 |
|------|------|------------|----------|------|
| GET | `/v1/groups/public` | `miniapp/main.py` | 公开群组列表（搜索、筛选、分页） | JWT（可选） |
| GET | `/v1/groups/public/{group_id}` | `miniapp/main.py` | 群组详情 | JWT（可选） |
| POST | `/v1/groups/public` | `miniapp/main.py` | 创建公开群组（扣星） | JWT |
| PATCH | `/v1/groups/public/{group_id}` | `miniapp/main.py` | 更新群组信息 | JWT |
| POST | `/v1/groups/public/{group_id}/join` | `miniapp/main.py` | 加入群组（发放进入奖励） | JWT |
| POST | `/v1/groups/public/{group_id}/bookmark` | `miniapp/main.py` | 收藏群组 | JWT |
| DELETE | `/v1/groups/public/{group_id}/bookmark` | `miniapp/main.py` | 取消收藏群组 | JWT |
| GET | `/v1/groups/public/bookmarks` | `miniapp/main.py` | 收藏群组列表 | JWT |
| GET | `/v1/groups/public/history` | `miniapp/main.py` | 用户群组历史记录 | JWT |
| POST | `/v1/groups/public/{group_id}/pin` | `miniapp/main.py` | 置顶群组（管理员） | JWT（管理员） |
| POST | `/v1/groups/public/{group_id}/unpin` | `miniapp/main.py` | 取消置顶群组（管理员） | JWT（管理员） |
| GET | `/v1/groups/public/{group_id}/invite_link` | `miniapp/main.py` | 获取群组邀请链接 | JWT |
| POST | `/v1/groups/public/{group_id}/report` | `miniapp/main.py` | 举报群组 | JWT |
| POST | `/v1/groups/public/{group_id}/events` | `miniapp/main.py` | 记录群组事件（浏览、点击等） | JWT（可选） |
| GET | `/v1/groups/public/stats/summary` | `miniapp/main.py` | 群组转化统计（管理员） | JWT（管理员） |

---

### 公开群组活动

| 方法 | 路径 | 控制器文件 | 主要用途 | 鉴权 |
|------|------|------------|----------|------|
| GET | `/v1/groups/public/activities` | `miniapp/main.py` | 活动列表 | JWT（可选） |
| GET | `/v1/groups/public/activities/{activity_id}` | `miniapp/main.py` | 活动详情 | JWT（可选） |
| GET | `/v1/groups/public/activities/{activity_id}/webhooks` | `miniapp/main.py` | 活动 Webhook 列表（管理员） | JWT（管理员） |
| POST | `/v1/groups/public/activities/{activity_id}/webhooks` | `miniapp/main.py` | 创建/更新活动 Webhook（管理员） | JWT（管理员） |
| DELETE | `/v1/groups/public/activities/webhooks/{webhook_id}` | `miniapp/main.py` | 删除活动 Webhook（管理员） | JWT（管理员） |

---

## 鉴权说明

### Web Admin 鉴权

- **Session Cookie**: 通过 `/admin/login` 登录后，设置 Session Cookie，后续请求自动携带
- **需登录**: 标记为"需登录"的接口需要有效的 Session Cookie
- **管理员**: 标记为"需登录（管理员）"的接口需要管理员权限（`ADMIN_IDS` 或 `SUPER_ADMINS`）

### MiniApp API 鉴权

- **JWT Token**: 通过 `/api/auth/login` 获取 JWT Token，后续请求在 `Authorization: Bearer <token>` 头中携带
- **JWT（可选）**: 接口可以匿名访问，但如果提供 Token 会返回个性化数据（如收藏状态）
- **JWT（管理员）**: 需要管理员权限（Token 中的 `is_admin: true` 或用户 ID 在 `ADMIN_IDS` 中）

### 无需鉴权

- 健康检查端点（`/healthz`、`/readyz`、`/metrics`）
- 登录页面和登录接口
- 部分公开数据接口（如 `/admin/api/v1/dashboard/public`）

---

## 快速查找

### 按功能查找

- **Dashboard 数据**: `/admin/api/v1/dashboard`, `/admin/api/v1/dashboard/public`
- **任务列表**: `/admin/api/v1/tasks`
- **群组列表**: `/admin/api/v1/group-list`, `/v1/groups/public`
- **统计数据**: `/admin/api/v1/stats`, `/admin/api/v1/stats/overview`
- **审计日志**: `/admin/api/v1/audit`
- **系统日志**: `/admin/api/v1/logs`
- **系统设置**: `/admin/api/v1/settings`
- **用户登录**: `/api/auth/login` (MiniApp), `/admin/login` (Web Admin)

---

*最后更新: 2025-01-XX*

