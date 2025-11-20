# 🚀 自动部署指南

## 📋 概述

本文档提供一键部署命令和完整的部署流程说明，实现：**构建镜像 → 启动服务 → 执行全栈测试 → 生成报告**。

---

## ⚡ 快速开始

### 本地开发环境

```powershell
# 准备 .env.local（参考 ENV-CONFIG-GUIDE.md）
.\docs\deployment\deploy-local.ps1
```

**一条命令完成**:
1. ✅ 构建 Docker 镜像
2. ✅ 启动所有服务（数据库、后端 API、前端）
3. ✅ 等待服务就绪
4. ✅ 执行全栈测试（后端 API + 前端 smoke test）
5. ✅ 生成 HTML 测试报告
6. ✅ 返回退出码（成功：0，失败：非 0）

### 生产环境

```powershell
# 在服务器上执行
# 准备 .env.production（参考 ENV-CONFIG-GUIDE.md）
.\docs\deployment\deploy-production.ps1
```

**一条命令完成**:
1. ✅ 拉取/构建最新镜像
2. ✅ 启动生产服务
3. ✅ 等待服务就绪
4. ✅ 执行全栈测试（针对生产地址）
5. ✅ 生成 HTML 测试报告
6. ✅ 返回退出码（成功：0，失败：非 0）

---

## ⚡ 一键命令总览

### 本地开发环境

```powershell
# 首次准备：手动创建 .env.local 文件
# ⚠️ 注意：.env 文件被 Git 忽略，需要手动创建
# 参考 docs/deployment/ENV-CONFIG-GUIDE.md 中的模板
# 至少填写：BOT_TOKEN, ADMIN_IDS, POSTGRES_PASSWORD, MINIAPP_JWT_SECRET, ADMIN_SESSION_SECRET, ADMIN_WEB_PASSWORD

# 一键部署（包含测试）
.\docs\deployment\deploy-local.ps1
```

**功能**:
- ✅ 构建 Docker 镜像
- ✅ 启动所有服务（Web Admin API、MiniApp API、Frontend、Database）
- ✅ 等待服务就绪
- ✅ 自动执行全栈测试
- ✅ 生成测试报告

### 生产环境

```powershell
# 在服务器上执行

# 首次准备：手动创建 .env.production 文件
# ⚠️ 注意：.env 文件被 Git 忽略，需要手动创建
# 参考 docs/deployment/ENV-CONFIG-GUIDE.md 中的模板
# 必须填写真实的配置值（特别是敏感信息）：
#   - BOT_TOKEN（真实 Token）
#   - ADMIN_IDS（真实管理员 ID）
#   - POSTGRES_PASSWORD（强密码，至少16位）
#   - MINIAPP_JWT_SECRET（随机64位十六进制）
#   - ADMIN_SESSION_SECRET（随机64位十六进制）
#   - ADMIN_WEB_PASSWORD（强密码）
#   - NEXT_PUBLIC_ADMIN_API_BASE_URL（公网 IP 或域名）
#   - NEXT_PUBLIC_MINIAPP_API_BASE_URL（公网 IP 或域名）

# 设置文件权限（保护敏感信息）
chmod 600 .env.production

# 一键部署（包含测试）
.\docs\deployment\deploy-production.ps1
```

**功能**:
- ✅ 拉取最新镜像（可选）
- ✅ 启动生产服务
- ✅ 等待服务就绪
- ✅ 自动执行全栈测试（针对生产地址）
- ✅ 生成测试报告
- ✅ 如果测试失败，部署会返回非零退出码

---

## 📊 部署后测试报告位置

部署完成后，完整测试报告位于：

**统一 HTML 报告**（推荐查看）:
```
docs/api-testing/output/full-stack-test-YYYYMMDD-HHMMSS/full-stack-test-report.html
```

**其他测试文件**:
- `summary.json` - 测试汇总 JSON
- `summary.csv` - 测试汇总 CSV
- `backend-pytest-report.html` - 后端 pytest HTML 报告
- `frontend-smoke-test-report.html` - 前端 smoke test HTML 报告
- `api-powershell-tests.csv` - PowerShell API 测试结果
- `api-powershell-error.log` - PowerShell 测试错误日志
- `backend-pytest-output.log` - 后端 pytest 输出日志
- `frontend-smoke-test-output.log` - 前端测试输出日志

**示例路径**:
```
docs/api-testing/output/full-stack-test-20251115-143022/
├── full-stack-test-report.html        # ⭐ 统一 HTML 报告
├── summary.json
├── summary.csv
├── backend-pytest-report.html
├── frontend-smoke-test-report.html
├── api-powershell-tests.csv
└── 其他日志文件...
```

---

## 🔧 本地部署详解

### 前置条件

1. ✅ **安装 Docker 和 Docker Compose**
   ```bash
   # 验证安装
   docker --version
   docker-compose --version
   ```

2. ✅ **准备环境变量文件**
   ```powershell
   # 复制模板
   Copy-Item .env.local.example .env.local
   
   # 编辑 .env.local，至少填写：
   # - BOT_TOKEN
   # - ADMIN_IDS
   # - POSTGRES_PASSWORD（如果使用 PostgreSQL）
   ```

3. ✅ **准备 Docker Compose 覆盖文件**（可选，用于本地开发）
   ```powershell
   Copy-Item docker-compose.override.yml.example docker-compose.override.yml
   ```

### 执行部署

```powershell
# 基本部署（包含测试）
.\docs\deployment\deploy-local.ps1

# 跳过测试
.\docs\deployment\deploy-local.ps1 -SkipTests

# 跳过构建（使用已有镜像）
.\docs\deployment\deploy-local.ps1 -SkipBuild

# 使用自定义环境文件
.\docs\deployment\deploy-local.ps1 -EnvFile ".env.dev"
```

### 部署流程

1. **检查环境文件** - 加载 `.env.local`（如果存在）
2. **构建 Docker 镜像** - 构建所有服务的镜像
3. **启动服务** - 使用 `docker-compose` 启动所有服务
4. **等待服务就绪** - 检查健康检查端点（最多等待 60 秒）
5. **执行全栈测试** - 运行 `docs/api-testing/run-full-stack-tests.ps1`
6. **生成测试报告** - 自动生成 HTML 报告
7. **显示部署摘要** - 输出服务地址和测试报告路径

### 访问服务

部署成功后，可以访问：

- **Web Admin API**: http://localhost:8000
  - 健康检查: http://localhost:8000/healthz
  - Dashboard: http://localhost:8000/admin/dashboard
  - OpenAPI Schema: http://localhost:8000/openapi.json

- **MiniApp API**: http://localhost:8080
  - 健康检查: http://localhost:8080/healthz
  - OpenAPI Schema: http://localhost:8080/openapi.json

- **Frontend**: http://localhost:3001

### 停止服务

```powershell
# 停止服务（保留数据卷）
docker-compose -f docker-compose.yml down

# 停止服务并删除数据卷
docker-compose -f docker-compose.yml down -v
```

---

## 🌐 生产环境部署详解

### 前置条件

1. ✅ **服务器已安装 Docker 和 Docker Compose**
2. ✅ **服务器已配置防火墙/安全组**（开放 8000、8080 端口）
3. ✅ **准备生产环境变量文件**
   ```powershell
   # 在服务器上
   Copy-Item .env.production.example .env.production
   
   # 编辑 .env.production，填入真实配置：
   # - BOT_TOKEN（真实 Token）
   # - ADMIN_IDS（真实管理员 ID）
   # - POSTGRES_PASSWORD（强密码）
   # - MINIAPP_JWT_SECRET（随机 64 位十六进制）
   # - ADMIN_SESSION_SECRET（随机 64 位十六进制）
   # - ADMIN_WEB_PASSWORD（强密码）
   # - NEXT_PUBLIC_ADMIN_API_BASE_URL（公网 IP 或域名）
   # - NEXT_PUBLIC_MINIAPP_API_BASE_URL（公网 IP 或域名）
   ```

### 执行部署

```powershell
# 基本部署（包含测试）
.\docs\deployment\deploy-production.ps1

# 跳过测试
.\docs\deployment\deploy-production.ps1 -SkipTests

# 跳过拉取镜像（使用已有镜像）
.\docs\deployment\deploy-production.ps1 -SkipPull

# 指定测试目标地址
.\docs\deployment\deploy-production.ps1 -AdminBaseUrl "http://165.154.233.55:8000" -MiniAppBaseUrl "http://165.154.233.55:8080"
```

### 部署流程

1. **检查环境文件** - 加载 `.env.production`（如果存在）
2. **拉取最新镜像** - 从注册表拉取最新镜像（可选）
3. **启动服务** - 使用 `docker-compose.production.yml` 启动生产服务
4. **等待服务就绪** - 检查健康检查端点（最多等待 90 秒）
5. **执行全栈测试** - 运行全栈测试（针对生产地址）
6. **生成测试报告** - 自动生成 HTML 报告
7. **验证部署** - 如果测试失败，返回非零退出码

### 访问服务

部署成功后，可以访问：

- **Web Admin API**: `http://<生产IP>:8000` 或 `https://api.yourdomain.com`
- **MiniApp API**: `http://<生产IP>:8080` 或 `https://miniapp-api.yourdomain.com`

---

## 🔄 CI/CD 流程概览

### 自动触发

当代码推送到 `main` 或 `release/*` 分支时，GitHub Actions 自动执行：

1. ✅ **构建和测试**（`build-and-test` job）
   - 构建 Docker 镜像
   - 启动服务
   - 执行全栈测试
   - 上传测试报告

2. ✅ **生产部署**（`deploy-production` job，仅 `main` 分支）
   - SSH 到生产服务器
   - 执行 `deploy-production.ps1`
   - 验证部署

### 查看 CI/CD 结果

1. 进入 GitHub 仓库
2. 点击 **Actions** 标签
3. 选择对应的运行
4. 查看构建日志和测试报告

---

## 📝 需要人工填写的配置项

### 本地开发环境 (`.env.local`)

| 配置项 | 说明 | 必填 | 默认值 |
|-------|------|------|--------|
| `BOT_TOKEN` | Telegram Bot Token | ✅ 是 | - |
| `ADMIN_IDS` | 管理员 Telegram ID | ✅ 是 | - |
| `POSTGRES_PASSWORD` | 数据库密码（如果使用 PostgreSQL） | ⚠️ 使用 PostgreSQL 时 | `redpacket123` |
| `MINIAPP_JWT_SECRET` | JWT 密钥 | ✅ 是 | - |
| `ADMIN_SESSION_SECRET` | 会话密钥 | ✅ 是 | - |
| `ADMIN_WEB_PASSWORD` | Web 管理员密码 | ✅ 是 | - |

### 生产环境 (`.env.production`)

| 配置项 | 说明 | 必填 | 安全要求 |
|-------|------|------|---------|
| `BOT_TOKEN` | Telegram Bot Token | ✅ 是 | 真实 Token |
| `ADMIN_IDS` | 管理员 Telegram ID | ✅ 是 | 真实 ID |
| `POSTGRES_PASSWORD` | 数据库密码 | ✅ 是 | 至少 16 位，强密码 |
| `MINIAPP_JWT_SECRET` | JWT 密钥 | ✅ 是 | 随机 64 位十六进制 |
| `ADMIN_SESSION_SECRET` | 会话密钥 | ✅ 是 | 随机 64 位十六进制 |
| `ADMIN_WEB_PASSWORD` | Web 管理员密码 | ✅ 是 | 至少 8 位，强密码 |
| `NEXT_PUBLIC_ADMIN_API_BASE_URL` | 前端 Admin API 地址 | ✅ 是 | 公网 IP 或域名 |
| `NEXT_PUBLIC_MINIAPP_API_BASE_URL` | 前端 MiniApp API 地址 | ✅ 是 | 公网 IP 或域名 |

**⚠️ 重要**: 所有标记为「必填」的配置项必须填写真实值，不能使用占位符。

---

## 🎯 部署与测试策略

### 每次部署自动执行的测试

1. **健康检查测试**
   - `/healthz` - 基础健康检查
   - `/readyz` - 就绪检查（数据库连接等）

2. **API 端点测试**
   - OpenAPI Schema 验证
   - Dashboard 公开数据接口
   - 公开群组列表接口

3. **性能测试**
   - 响应时间测量
   - 平均响应时间统计

### 阻断部署的测试失败

以下测试失败会**阻止**部署继续：

- ❌ 健康检查失败（`/healthz` 返回非 200）
- ❌ 就绪检查失败（`/readyz` 返回非 200）
- ❌ 后端 pytest 核心测试失败（数据库连接、基本 API 端点）

### 仅作为告警的测试失败

以下测试失败**不会阻止**部署，但会标记为警告：

- ⚠️ 部分 PowerShell 测试失败（某些端点不可用，但核心功能正常）
- ⚠️ 性能指标超出阈值（响应时间过长，但功能正常）

---

## 🔍 故障排查

### 问题 1: 服务无法启动

**症状**: Docker Compose 启动失败

**排查步骤**:
1. 检查 Docker 日志: `docker-compose logs`
2. 检查环境变量: `docker-compose config`
3. 检查端口占用: `netstat -ano | findstr :8000`

### 问题 2: 健康检查失败

**症状**: `/healthz` 返回 500 或超时

**排查步骤**:
1. 检查服务日志: `docker-compose logs web_admin`
2. 检查数据库连接: `docker-compose exec web_admin env | grep DATABASE_URL`
3. 检查服务状态: `docker-compose ps`

### 问题 3: 测试失败

**症状**: 全栈测试返回失败

**排查步骤**:
1. 查看测试报告: `docs/api-testing/output/full-stack-test-*/full-stack-test-report.html`
2. 检查错误日志: `docs/api-testing/output/full-stack-test-*/backend-pytest-output.log`
3. 手动测试端点: `curl http://localhost:8000/healthz`

### 问题 4: 前端无法连接后端

**症状**: 前端页面无法加载数据

**排查步骤**:
1. 检查前端环境变量: `docker-compose exec frontend env | grep NEXT_PUBLIC`
2. 检查后端地址是否正确: 前端访问的地址应该是后端实际监听地址
3. 检查网络连接: 前端容器是否能访问后端容器

---

## 📚 相关文档

- [部署现状分析](DEPLOYMENT-CURRENT-STATE.md) - 当前部署架构
- [环境变量配置指南](ENV-CONFIG-GUIDE.md) - 环境变量详细说明
- [CI/CD 集成指南](CI-CD-GUIDE.md) - GitHub Actions 配置说明
- [全栈测试指南](../api-testing/README-FULL-STACK-TESTING.md) - 测试框架使用说明

---

## 🔄 更新日志

- **2025-11-15**: 创建自动部署框架
  - 添加本地部署脚本
  - 添加生产部署脚本
  - 添加 CI/CD 配置
  - 添加环境变量模板

---

**最后更新**: 2025-11-15

