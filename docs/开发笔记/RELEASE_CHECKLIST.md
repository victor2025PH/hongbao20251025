# 发布前检查清单

本文档提供发布前的完整检查清单，确保新版本可以安全部署到生产环境。

---

## 目录

- [依赖安装与构建](#依赖安装与构建)
- [测试](#测试)
- [本地/测试环境验收](#本地测试环境验收)
- [安全项](#安全项)
- [回滚策略](#回滚策略)

---

## 依赖安装与构建

### Python 依赖

- [ ] **安装依赖**:
  ```bash
  pip install -r requirements.txt
  ```
  预期: 所有依赖成功安装，无错误

- [ ] **检查依赖版本冲突**:
  ```bash
  pip check
  ```
  预期: 无冲突报告

- [ ] **验证关键依赖版本**:
  - FastAPI: `>= 0.115.0`
  - SQLAlchemy: `>= 2.0.44`
  - aiogram: `>= 3.22.0`
  - PyJWT: `>= 2.9.0`

---

### 前端依赖

- [ ] **安装依赖**:
  ```bash
  cd frontend-next
  npm install
  ```
  预期: 所有依赖成功安装，无错误

- [ ] **检查依赖版本冲突**:
  ```bash
  npm audit
  ```
  预期: 无高危漏洞（中低危可接受）

- [ ] **构建生产版本**:
  ```bash
  npm run build
  ```
  预期: 构建成功，无错误或警告

- [ ] **验证构建产物**:
  ```bash
  ls -la frontend-next/.next
  ```
  预期: `.next` 目录存在且包含构建产物

---

## 测试

### 单元测试

- [ ] **运行所有测试**:
  ```bash
  pytest tests/ -v
  ```
  预期: 所有测试通过（退出码 0）

- [ ] **运行关键测试模块**:
  ```bash
  pytest tests/test_regression_features.py -v
  pytest tests/test_public_group_service.py -v
  pytest tests/test_api_public_groups.py -v
  pytest tests/test_miniapp_auth.py -v
  ```
  预期: 所有测试通过

---

### 集成测试

- [ ] **运行完整自检脚本**:
  ```bash
  python scripts/self_check.py
  ```
  预期: 所有步骤通过（`"ok": true`）

- [ ] **环境变量检查**:
  ```bash
  python scripts/check_env.py
  ```
  预期: 所有必需环境变量都存在

---

### 关键场景测试

#### 红包发放场景

- [ ] **创建红包任务**:
  - 通过 Web Admin 创建红包任务
  - 验证任务状态为 `pending`
  - 验证任务处理成功，状态变为 `success`

- [ ] **发送红包**:
  - 验证红包成功发送到目标群组
  - 验证用户收到红包
  - 验证余额正确扣减

- [ ] **失败处理**:
  - 测试余额不足的情况
  - 测试用户不存在的情况
  - 验证错误信息正确记录

---

#### 充值场景

- [ ] **创建充值订单**:
  - 通过前端创建充值订单
  - 验证订单状态为 `pending`
  - 验证订单金额和币种正确

- [ ] **IPN 回调处理**:
  - 模拟 NowPayments IPN 回调
  - 验证订单状态更新为 `success`
  - 验证用户余额正确增加
  - 验证审计日志正确记录

- [ ] **订单超时处理**:
  - 测试订单过期逻辑
  - 验证过期订单状态更新为 `expired`

---

#### 公开群组场景

- [ ] **创建公开群组**:
  - 通过 MiniApp API 创建群组
  - 验证群组状态为 `active`
  - 验证用户余额正确扣减（创建费用）
  - 验证风险评分计算正确

- [ ] **加入群组**:
  - 通过 MiniApp API 加入群组
  - 验证进入奖励正确发放
  - 验证奖励池正确扣减

- [ ] **群组列表**:
  - 验证群组列表正确返回
  - 验证搜索和筛选功能正常
  - 验证分页功能正常

---

#### 认证场景

- [ ] **MiniApp 登录**:
  - 使用 Telegram `initData` 登录
  - 验证 JWT Token 正确生成
  - 验证 Token 可以用于后续 API 调用

- [ ] **Web Admin 登录**:
  - 使用用户名和密码登录
  - 验证会话 Cookie 正确设置
  - 验证登录后可以访问受保护页面

- [ ] **权限验证**:
  - 测试非管理员无法访问管理页面
  - 测试超管可以访问所有页面

---

## 本地/测试环境验收

### 后端服务验收

- [ ] **Web Admin 健康检查**:
  ```bash
  curl http://localhost:8000/healthz
  ```
  预期: `{"ok": true, "ts": "..."}`

- [ ] **Web Admin 就绪检查**:
  ```bash
  curl http://localhost:8000/readyz
  ```
  预期: `{"ready": true, "checks": {...}}`

- [ ] **MiniApp API 健康检查**:
  ```bash
  curl http://localhost:8080/healthz
  ```
  预期: `{"ok": true}`

- [ ] **Dashboard API**:
  ```bash
  curl http://localhost:8000/admin/api/v1/dashboard/public
  ```
  预期: 返回 JSON 数据，包含 `user_count`、`active_envelopes` 等字段

---

### 前端控制台验收

- [ ] **Dashboard 页面** (`http://localhost:3001/`):
  - 页面正常加载
  - 统计卡片显示数据（真实或 mock）
  - 趋势图显示（如果有数据）
  - 无 JavaScript 错误

- [ ] **任务列表页面** (`http://localhost:3001/tasks`):
  - 页面正常加载
  - 可以搜索任务
  - 可以筛选状态
  - 可以分页
  - 点击任务可以查看详情

- [ ] **群组列表页面** (`http://localhost:3001/groups`):
  - 页面正常加载
  - 可以搜索群组
  - 可以筛选标签
  - 可以分页
  - 点击群组可以查看详情

- [ ] **红包统计页面** (`http://localhost:3001/stats`):
  - 页面正常加载
  - 统计图表显示
  - 无 JavaScript 错误

- [ ] **日志中心页面** (`http://localhost:3001/logs`):
  - 页面正常加载
  - 可以查看系统日志
  - 可以查看审计日志

- [ ] **系统设置页面** (`http://localhost:3001/settings`):
  - 页面正常加载
  - 可以查看当前设置
  - 可以保存设置（如果已实现）

---

### Web Admin 页面验收

- [ ] **登录页面** (`http://localhost:8000/admin/login`):
  - 登录表单正常显示
  - 可以输入用户名和密码
  - 登录后跳转到 Dashboard

- [ ] **Dashboard 页面** (`http://localhost:8000/admin/dashboard`):
  - 页面正常加载
  - 统计卡片显示数据
  - 图表显示正常

- [ ] **公开群组页面** (`http://localhost:8000/admin/public-groups`):
  - 页面正常加载
  - 可以查看群组列表
  - 可以审核群组

- [ ] **用户列表页面** (`http://localhost:8000/admin/users`):
  - 页面正常加载
  - 可以查看用户列表
  - 可以查看用户详情

---

### 功能按钮验收

- [ ] **创建红包任务按钮**:
  - 点击按钮可以打开创建表单
  - 填写表单后可以提交
  - 提交后任务成功创建

- [ ] **保存设置按钮**:
  - 修改设置后点击保存
  - 设置成功保存
  - 页面显示成功提示

- [ ] **搜索功能**:
  - 在搜索框输入关键词
  - 搜索结果正确显示
  - 清空搜索后恢复原始列表

- [ ] **筛选功能**:
  - 选择筛选条件
  - 列表正确筛选
  - 清除筛选后恢复原始列表

---

## 安全项

### 敏感信息检查

- [ ] **确认 secrets/ 目录不被提交**:
  ```bash
  git ls-files | grep secrets/
  ```
  预期: 无输出（`secrets/` 目录应在 `.gitignore` 中）

- [ ] **确认 .env 文件不被提交**:
  ```bash
  git ls-files | grep "\.env$"
  ```
  预期: 无输出（`.env` 文件应在 `.gitignore` 中）

- [ ] **确认硬编码密钥**:
  ```bash
  grep -r "BOT_TOKEN.*=" --include="*.py" --exclude-dir=__pycache__ | grep -v "os.getenv"
  ```
  预期: 无输出（不应有硬编码的密钥）

---

### 认证与授权

- [ ] **Web Admin 必须登录才能访问**:
  - 未登录时访问 `/admin/dashboard` 应跳转到 `/admin/login`
  - 未登录时访问 `/admin/api/v1/dashboard` 应返回 401

- [ ] **MiniApp API 需要 JWT Token**:
  - 未提供 Token 时访问 `/v1/groups/public` 应返回 401
  - 提供无效 Token 时应返回 401

- [ ] **管理员权限验证**:
  - 非管理员无法访问管理接口
  - 超管可以访问所有接口

---

### 安全响应头

- [ ] **检查安全响应头**:
  ```bash
  curl -I http://localhost:8000/admin/login | grep -E "(X-Frame-Options|X-Content-Type-Options|Content-Security-Policy)"
  ```
  预期: 包含安全响应头

- [ ] **CSP 策略**:
  - 检查 `ADMIN_CSP` 环境变量是否配置
  - 验证 CSP 策略不会阻止正常功能

---

### 输入验证

- [ ] **SQL 注入防护**:
  - 所有数据库查询使用参数化查询（SQLAlchemy ORM）
  - 不使用字符串拼接构建 SQL

- [ ] **XSS 防护**:
  - 所有用户输入在输出前进行转义
  - 使用 Jinja2 模板的自动转义功能

- [ ] **CSRF 防护**:
  - Web Admin 表单包含 CSRF Token
  - API 使用 JWT Token 或 Session Cookie

---

## 回滚策略

### 代码回滚

**Git 回滚**:
```bash
# 1. 查看提交历史
git log --oneline -10

# 2. 回滚到上一个版本
git checkout <previous-commit-hash>

# 3. 强制推送到远程（谨慎操作）
git push --force origin main
```

**注意事项**:
- 回滚前备份当前数据库
- 回滚后需要重启所有服务
- 通知团队成员回滚操作

---

### 数据库回滚

**如果新版本包含数据库迁移**:

1. **备份当前数据库**:
   ```bash
   # SQLite
   cp data.sqlite data.sqlite.backup-$(date +%Y%m%d-%H%M%S)
   
   # PostgreSQL
   pg_dump -U user hongbao_db > backup-$(date +%Y%m%d-%H%M%S).sql
   
   # MySQL
   mysqldump -u user -p hongbao_db > backup-$(date +%Y%m%d-%H%M%S).sql
   ```

2. **恢复数据库**:
   ```bash
   # SQLite
   cp data.sqlite.backup-YYYYMMDD-HHMMSS data.sqlite
   
   # PostgreSQL
   psql -U user -d hongbao_db < backup-YYYYMMDD-HHMMSS.sql
   
   # MySQL
   mysql -u user -p hongbao_db < backup-YYYYMMDD-HHMMSS.sql
   ```

**注意事项**:
- 数据库回滚可能导致数据丢失（如果新版本已写入数据）
- 建议在低峰期执行回滚
- 回滚后验证数据完整性

---

### 服务回滚

**Docker 回滚**:
```bash
# 1. 停止当前容器
docker-compose down

# 2. 切换到上一个版本的镜像
docker-compose up -d --image <previous-image-tag>
```

**Systemd 回滚**:
```bash
# 1. 停止当前服务
systemctl stop hongbao-web-admin
systemctl stop hongbao-miniapp-api

# 2. 切换到上一个版本
cd /path/to/previous/version

# 3. 启动服务
systemctl start hongbao-web-admin
systemctl start hongbao-miniapp-api
```

---

### 回滚验证

回滚后需要验证:

- [ ] **服务健康检查**:
  ```bash
  curl http://localhost:8000/healthz
  curl http://localhost:8080/healthz
  ```
  预期: 两个服务都返回 `{"ok": true}`

- [ ] **关键功能测试**:
  - 登录功能正常
  - Dashboard 数据正常显示
  - 红包发送功能正常
  - 充值功能正常

- [ ] **数据完整性**:
  - 检查用户数据是否完整
  - 检查订单数据是否完整
  - 检查账本数据是否完整

---

## 发布流程

### 1. 预发布检查

- [ ] 完成所有测试
- [ ] 完成本地/测试环境验收
- [ ] 完成安全项检查
- [ ] 准备回滚方案

### 2. 发布到生产

- [ ] 备份生产数据库
- [ ] 备份生产代码
- [ ] 部署新版本代码
- [ ] 运行数据库迁移（如果有）
- [ ] 重启所有服务

### 3. 发布后验证

- [ ] 验证服务健康检查
- [ ] 验证关键功能
- [ ] 监控错误日志
- [ ] 监控性能指标

### 4. 回滚（如果需要）

- [ ] 确认问题无法快速修复
- [ ] 执行回滚操作
- [ ] 验证回滚后服务正常
- [ ] 记录问题原因和解决方案

---

## TODO

- [ ] 添加自动化发布脚本
- [ ] 添加发布前自动检查脚本
- [ ] 添加发布后自动验证脚本
- [ ] 添加回滚自动化脚本
- [ ] 添加发布通知机制（Slack/Email）

---

*最后更新: 2025-01-XX*

