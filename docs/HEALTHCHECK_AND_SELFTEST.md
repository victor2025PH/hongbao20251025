# 健康检查与自检脚本说明

本文档说明所有健康检查端点、自检脚本的用途和执行顺序，以及本地启动后的手动验证步骤。

---

## 目录

- [健康检查端点](#健康检查端点)
- [自检脚本说明](#自检脚本说明)
- [推荐执行顺序](#推荐执行顺序)
- [本地启动后验证步骤](#本地启动后验证步骤)

---

## 健康检查端点

### Web Admin (端口 8000)

#### `/healthz` - 基础健康检查

**路径**: `GET /healthz`  
**认证**: 无需认证  
**响应示例**:
```json
{
  "ok": true,
  "ts": "2025-01-XXT12:00:00.000000"
}
```

**用途**: 
- 快速检查服务是否运行
- 负载均衡器/监控系统使用
- 返回当前 UTC 时间戳

**验证命令**:
```bash
curl http://localhost:8000/healthz
```

---

#### `/readyz` - 就绪检查

**路径**: `GET /readyz`  
**认证**: 无需认证  
**响应示例**:
```json
{
  "ready": true,
  "checks": {
    "static_dir": true,
    "templates": true,
    "database": true
  }
}
```

**用途**:
- 检查服务是否就绪（静态目录、模板目录、数据库连接）
- Kubernetes 就绪探针使用

**验证命令**:
```bash
curl http://localhost:8000/readyz
```

---

#### `/metrics` - Prometheus 指标

**路径**: `GET /metrics`  
**认证**: 无需认证  
**响应格式**: Prometheus 文本格式

**用途**:
- Prometheus 监控系统采集指标
- 应用运行时间、自定义业务指标

**验证命令**:
```bash
curl http://localhost:8000/metrics
```

**示例输出**:
```
# HELP app_uptime_seconds Application uptime in seconds.
# TYPE app_uptime_seconds counter
app_uptime_seconds 3600
# HELP app_info Application info.
# TYPE app_info gauge
app_info{app="telegram-hongbao-web-admin"} 1
```

---

#### `/admin/api/v1/dashboard` - Dashboard 数据

**路径**: `GET /admin/api/v1/dashboard`  
**认证**: 需要管理员登录（Cookie Session）  
**响应**: Dashboard 统计数据 JSON

**用途**:
- 前端 Dashboard 页面数据源
- 验证数据库查询和业务逻辑

**验证命令**:
```bash
# 需要先登录获取 Cookie
curl -b cookies.txt http://localhost:8000/admin/api/v1/dashboard
```

---

#### `/admin/api/v1/dashboard/public` - Dashboard 数据（公开）

**路径**: `GET /admin/api/v1/dashboard/public`  
**认证**: 无需认证  
**响应**: Dashboard 统计数据 JSON（失败时返回 mock 数据）

**用途**:
- 前端 Dashboard 页面数据源（无需登录）
- 验证数据库查询和业务逻辑（带 mock fallback）

**验证命令**:
```bash
curl http://localhost:8000/admin/api/v1/dashboard/public
```

---

#### `/admin/api/v1/stats` - 趋势统计

**路径**: `GET /admin/api/v1/stats?days=7`  
**认证**: 需要管理员登录  
**响应**: 趋势统计数据 JSON

**用途**:
- 前端 Dashboard 趋势图表数据源
- 验证数据库聚合查询

**验证命令**:
```bash
curl -b cookies.txt "http://localhost:8000/admin/api/v1/stats?days=7"
```

---

### MiniApp API (端口 8080)

#### `/healthz` - 基础健康检查

**路径**: `GET /healthz`  
**认证**: 无需认证  
**响应示例**:
```json
{
  "ok": true
}
```

**用途**:
- 快速检查服务是否运行
- 负载均衡器/监控系统使用

**验证命令**:
```bash
curl http://localhost:8080/healthz
```

---

## 自检脚本说明

### `scripts/self_check.py` - 完整自检脚本

**用途**: 运行完整的自检流程，包括服务启动、健康检查、环境检查、测试用例

**执行方式**:
```bash
python scripts/self_check.py
```

**功能**:
1. **启动 Web Admin 服务**（如果 `SELF_CHECK_SKIP_SERVER=1` 则跳过）
2. **检查 `/healthz` 端点**（等待最多 15 秒）
3. **运行环境检查**（`scripts/check_env.py`）
4. **运行活动报告脚本**（`scripts/activity_report_cron.py`）
5. **运行关键测试用例**:
   - `tests/test_regression_features.py`
   - `tests/test_public_group_service.py`
   - `tests/test_api_public_groups.py`

**输出格式**: JSON
```json
{
  "ok": true,
  "steps": [
    {"name": "launch_app", "ok": true},
    {"name": "healthz", "ok": true},
    {"name": "check_env", "ok": true},
    {"name": "activity_report_cron", "ok": true},
    {"name": "pytest:tests/test_regression_features.py", "ok": true},
    {"name": "pytest:tests/test_public_group_service.py", "ok": true},
    {"name": "pytest:tests/test_api_public_groups.py", "ok": true}
  ]
}
```

**退出码**:
- `0`: 所有检查通过
- `1`: 至少一个检查失败

**环境变量**:
- `SELF_CHECK_SKIP_SERVER=1`: 跳过服务启动（假设服务已在运行）

---

### `scripts/check_env.py` - 环境变量检查

**用途**: 检查 `.env.example` 是否包含 `config/settings.py` 中声明的所有必需环境变量

**执行方式**:
```bash
python scripts/check_env.py
```

**功能**:
1. 加载 `.env.example` 文件
2. 解析 `config/settings.py` 中的 `Settings` 类
3. 检查所有必需的环境变量是否在 `.env.example` 中定义
4. 检查是否有重复的键

**输出**:
- `[OK] .env.example covers required keys.` - 所有键都存在
- `[ERROR] missing keys in .env.example:` - 缺少键列表

**退出码**:
- `0`: 所有必需键都存在
- `1`: 缺少必需键或检测到重复键
- `2`: 解析配置文件失败

---

### `scripts/cleanup_db.py` - 数据库清理脚本

**用途**: 清理数据库中所有表数据（⚠️ 仅限开发测试使用）

**执行方式**:
```bash
python scripts/cleanup_db.py
```

**功能**:
1. 初始化数据库（`init_db()`）
2. 提示确认（输入 `y` 继续）
3. 删除所有表（`Base.metadata.drop_all(engine)`）
4. 重新创建所有表（`Base.metadata.create_all(engine)`）

**警告**: 
- ⚠️ **仅限开发测试使用，生产环境请勿运行！**
- 会删除所有数据，无法恢复

---

### `scripts/seed_public_groups.py` - 初始化公开群组数据

**用途**: 创建测试用的公开群组和活动数据

**执行方式**:
```bash
python scripts/seed_public_groups.py --groups 3 --activities 3 --creator 900001
```

**参数**:
- `--groups`: 创建的群组数量（默认: 3）
- `--activities`: 创建的活动数量（默认: 3）
- `--creator`: 创建者的 Telegram ID（默认: 900000）
- `--prefix`: 群组名称前缀（默认: "測試交友 "）

**功能**:
1. 生成测试群组定义（名称、邀请链接、描述、标签等）
2. 生成测试活动定义（名称、奖励点数、时间范围等）
3. 使用服务层创建群组和活动（保持与生产逻辑一致）
4. 输出创建的群组 ID 和活动 ID

**输出示例**:
```
[seed] group id=1 name='測試交友 20250101 #01' status=active risk=0 flags=[]
[seed] activity id=1 name='MiniApp 星星加碼 #01'
Seed completed.
Groups created: 1, 2, 3
Activities created: 1, 2, 3
```

---

### `scripts/activity_report_cron.py` - 活动报告定时任务

**用途**: 生成活动报告（用于定时任务或手动执行）

**执行方式**:
```bash
python scripts/activity_report_cron.py --days 1 --json --include-webhooks
```

**参数**:
- `--days`: 统计天数（默认: 1）
- `--json`: 输出 JSON 格式
- `--include-webhooks`: 包含 Webhook 信息

**功能**:
1. 统计指定天数内的活动数据
2. 生成活动报告（JSON 或文本格式）
3. 可选包含 Webhook 信息

---

## 推荐执行顺序

### 首次部署

1. **环境变量检查**:
   ```bash
   python scripts/check_env.py
   ```

2. **数据库初始化**:
   ```bash
   python -c "from models.db import init_db; init_db()"
   ```

3. **初始化测试数据**（可选）:
   ```bash
   python scripts/seed_public_groups.py --groups 3 --activities 3
   ```

4. **启动服务**:
   ```bash
   # Web Admin
   uvicorn web_admin.main:app --host 0.0.0.0 --port 8000 --reload
   
   # MiniApp API
   uvicorn miniapp.main:app --host 0.0.0.0 --port 8080 --reload
   ```

5. **运行完整自检**:
   ```bash
   python scripts/self_check.py
   ```

---

### 日常开发验证

1. **快速健康检查**:
   ```bash
   curl http://localhost:8000/healthz
   curl http://localhost:8080/healthz
   ```

2. **运行关键测试**:
   ```bash
   pytest tests/test_regression_features.py -v
   ```

3. **环境变量检查**（修改配置后）:
   ```bash
   python scripts/check_env.py
   ```

---

### 发布前验证

1. **完整自检**:
   ```bash
   python scripts/self_check.py
   ```

2. **运行所有测试**:
   ```bash
   pytest tests/ -v
   ```

3. **手动验证关键页面**（见下方"本地启动后验证步骤"）

---

## 本地启动后验证步骤

### 5 分钟内快速验证

#### 1. 服务健康检查（30 秒）

```bash
# Web Admin
curl http://localhost:8000/healthz
# 预期: {"ok": true, "ts": "..."}

# MiniApp API
curl http://localhost:8080/healthz
# 预期: {"ok": true}
```

**预期结果**: 两个服务都返回 `{"ok": true}`

---

#### 2. 就绪检查（30 秒）

```bash
curl http://localhost:8000/readyz
# 预期: {"ready": true, "checks": {"static_dir": true, "templates": true, "database": true}}
```

**预期结果**: `ready: true`，所有检查项为 `true`

---

#### 3. 前端控制台访问（1 分钟）

**访问**: `http://localhost:3001`

**预期表现**:
- 页面正常加载，显示 Dashboard
- 导航栏显示：Dashboard、任务列表、群组列表、红包统计、日志中心、设置
- 如果后端未运行，显示黄色提示"当前展示的是模拟统计数据"

**验证点**:
- ✅ 页面无 JavaScript 错误（打开浏览器控制台检查）
- ✅ 导航链接可点击
- ✅ Dashboard 卡片显示数据（真实或 mock）

---

#### 4. Web Admin 登录页面（1 分钟）

**访问**: `http://localhost:8000/admin/login`

**预期表现**:
- 显示登录表单
- 可以输入用户名和密码
- 登录后跳转到 Dashboard

**验证点**:
- ✅ 登录表单正常显示
- ✅ 可以输入用户名和密码
- ✅ 登录后跳转到 `/admin/dashboard`

---

#### 5. Dashboard API 数据（1 分钟）

```bash
# 公开接口（无需登录）
curl http://localhost:8000/admin/api/v1/dashboard/public
# 预期: {"user_count": ..., "active_envelopes": ..., ...}

# 趋势统计（需要登录，先跳过）
# curl -b cookies.txt "http://localhost:8000/admin/api/v1/stats?days=7"
```

**预期结果**: 返回 JSON 数据，包含 `user_count`、`active_envelopes` 等字段

---

#### 6. 前端 Dashboard 数据加载（1 分钟）

**访问**: `http://localhost:3001`，打开浏览器开发者工具 → Network

**预期表现**:
- 页面加载时发起 API 请求到 `http://localhost:8000/admin/api/v1/dashboard`
- 如果后端运行，显示真实数据，无黄色警告
- 如果后端未运行，显示 mock 数据，显示黄色警告

**验证点**:
- ✅ API 请求成功（200）或失败时自动 fallback 到 mock
- ✅ Dashboard 卡片显示数据
- ✅ 趋势图显示（如果有数据）

---

#### 7. 任务列表页面（30 秒）

**访问**: `http://localhost:3001/tasks`

**预期表现**:
- 显示任务列表页面
- 可以搜索、筛选、分页
- 点击任务可以查看详情

**验证点**:
- ✅ 页面正常加载
- ✅ 搜索框可以输入
- ✅ 状态筛选器可以切换
- ✅ 分页按钮可以点击

---

#### 8. 群组列表页面（30 秒）

**访问**: `http://localhost:3001/groups`

**预期表现**:
- 显示群组列表
- 可以搜索、筛选、分页
- 点击群组可以查看详情

**验证点**:
- ✅ 页面正常加载
- ✅ 搜索框可以输入
- ✅ 标签筛选器可以切换
- ✅ 点击群组卡片跳转到详情页

---

### 完整验证清单

#### 后端服务

- [ ] Web Admin `/healthz` 返回 200
- [ ] Web Admin `/readyz` 返回 `ready: true`
- [ ] MiniApp API `/healthz` 返回 200
- [ ] Web Admin `/admin/api/v1/dashboard/public` 返回 JSON 数据
- [ ] Web Admin `/metrics` 返回 Prometheus 格式指标

#### 前端控制台

- [ ] Dashboard 页面 (`/`) 正常加载
- [ ] 任务列表页面 (`/tasks`) 正常加载
- [ ] 群组列表页面 (`/groups`) 正常加载
- [ ] 群组详情页面 (`/groups/[id]`) 正常加载
- [ ] 红包统计页面 (`/stats`) 正常加载
- [ ] 日志中心页面 (`/logs`) 正常加载
- [ ] 审计日志页面 (`/logs/audit`) 正常加载
- [ ] 系统设置页面 (`/settings`) 正常加载

#### 功能验证

- [ ] Dashboard 显示真实数据（后端运行时）
- [ ] Dashboard 显示 mock 数据并提示（后端未运行时）
- [ ] 任务列表可以搜索和筛选
- [ ] 群组列表可以搜索和筛选
- [ ] 设置页面可以保存配置（如果已实现）

#### 错误处理

- [ ] 后端关闭时，前端优雅降级（显示 mock 数据或错误提示）
- [ ] 404 页面显示友好错误信息
- [ ] 网络错误时显示重试按钮

---

## TODO

- [ ] 添加自动化测试脚本，覆盖所有健康检查端点
- [ ] 添加性能基准测试（响应时间、并发数）
- [ ] 添加数据库连接池健康检查
- [ ] 添加外部服务依赖检查（NowPayments、OpenAI 等）
- [ ] 添加前端构建验证脚本

---

*最后更新: 2025-01-XX*

