# 📊 部署现状分析

## 📋 文档摘要

**生成时间**: 2025-11-15  
**分析范围**: 后端服务、前端项目、Docker 配置、部署方案  
**目标**: 梳理当前部署架构，为自动化部署流水线做准备

---

## 1. 后端服务列表

### 1.1 核心后端服务

| 服务名称 | 端口 | 容器名称 | 构建文件 | 依赖 | 状态 |
|---------|------|---------|---------|------|------|
| **Web Admin API** | 8000 | `redpacket_web_admin` | `Dockerfile.backend` | PostgreSQL | ✅ 已配置 |
| **MiniApp API** | 8080 | `redpacket_miniapp_api` | `Dockerfile.backend` | PostgreSQL | ✅ 已配置 |
| **Telegram Bot** | - | `redpacket_bot` | `Dockerfile.backend` | PostgreSQL | ✅ 已配置 |

### 1.2 数据库与缓存

| 服务名称 | 端口 | 容器名称 | 镜像 | 状态 |
|---------|------|---------|------|------|
| **PostgreSQL** | 5432 (仅容器内) | `redpacket_db` | `postgres:15-alpine` | ✅ 已配置 |
| **Redis** | 6379 (仅容器内) | `redpacket_redis` | `redis:7-alpine` | ✅ 已配置（可选） |

### 1.3 监控服务

| 服务名称 | 端口 | 容器名称 | 镜像 | 状态 |
|---------|------|---------|------|------|
| **Prometheus** | 9090 (仅本地) | `redpacket_prometheus` | `prom/prometheus:latest` | ✅ 已配置 |
| **Grafana** | 3000 (仅本地) | `redpacket_grafana` | `grafana/grafana:latest` | ✅ 已配置 |

---

## 2. 前端项目列表

### 2.1 Next.js 管理后台

| 项目名称 | 端口 | 容器名称 | 构建文件 | 构建方式 | 状态 |
|---------|------|---------|---------|---------|------|
| **frontend-next** | 3001 | `redpacket_frontend` | `frontend-next/Dockerfile` | Docker 多阶段构建 | ✅ 已配置 |

**配置位置**:
- 环境变量: `NEXT_PUBLIC_ADMIN_API_BASE_URL`, `NEXT_PUBLIC_MINIAPP_API_BASE_URL`
- 配置文件: `frontend-next/next.config.ts`

**构建要求**:
- Node.js 环境
- 构建时需要注入环境变量（Next.js 公共变量）
- 输出 standalone 模式用于 Docker

### 2.2 MiniApp 前端

| 项目名称 | 框架 | 构建方式 | 状态 |
|---------|------|---------|------|
| **miniapp-frontend** | Vite | ⚠️ 未配置 Docker | ⚠️ 待配置 |

---

## 3. Docker 配置文件

### 3.1 Dockerfile

| 文件 | 用途 | 状态 |
|------|------|------|
| `Dockerfile.backend` | 后端服务（Web Admin + MiniApp + Bot） | ✅ 已存在 |
| `frontend-next/Dockerfile` | Next.js 前端 | ✅ 已存在 |

### 3.2 Docker Compose

| 文件 | 用途 | 状态 |
|------|------|------|
| `docker-compose.yml` | 本地开发配置 | ✅ 已存在 |
| `docker-compose.production.yml` | 生产环境配置 | ✅ 已存在 |
| `docker-compose.override.yml` | 本地覆盖配置 | ❌ 缺失，需创建 |

---

## 4. 部署方案现状

### 4.1 当前部署方案

| 方案 | 工具 | 配置文件 | 状态 |
|------|------|---------|------|
| **Docker Compose** | docker-compose | `docker-compose.production.yml` | ✅ 已配置 |
| **自动化脚本** | Shell 脚本 | `deploy/scripts/deploy.sh` | ✅ 已存在 |
| **远程部署** | SSH + Shell | `deploy/scripts/deploy_remote.sh` | ✅ 已存在 |
| **CI/CD** | GitHub Actions | `.github/workflows/` | ❌ 缺失 |

### 4.2 部署流程

**当前流程**:
1. ✅ 使用 `docker-compose.production.yml` 启动服务
2. ✅ 手动执行 `docs/api-testing/run-full-stack-tests.ps1` 进行测试
3. ⚠️ 缺少自动化部署 + 测试一体化流程

**缺失功能**:
- ❌ 一键部署脚本（本地 + 生产）
- ❌ 自动测试集成（部署后自动执行全栈测试）
- ❌ CI/CD 流水线（GitHub Actions）
- ❌ 环境变量统一管理（`.env.example` 模板）

---

## 5. 端口映射与服务拓扑

### 5.1 端口映射

| 服务 | 容器端口 | 主机端口 | 绑定地址 | 用途 |
|------|---------|---------|---------|------|
| Web Admin API | 8000 | 8000 | `0.0.0.0` | 管理后台 API |
| MiniApp API | 8080 | 8080 | `0.0.0.0` | 小程序 API |
| Frontend | 3001 | 3001 | `127.0.0.1` | Next.js 前端（可通过 Nginx 代理） |
| PostgreSQL | 5432 | 5432 | `127.0.0.1` | 数据库（仅本地访问） |
| Redis | 6379 | 6379 | `127.0.0.1` | 缓存（仅本地访问） |
| Prometheus | 9090 | 9090 | `127.0.0.1` | 监控指标 |
| Grafana | 3000 | 3000 | `127.0.0.1` | 监控可视化 |

### 5.2 服务拓扑图

```
┌─────────────────────────────────────────────────────────────┐
│                        外部访问                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────┐          ┌────────▼────────┐
│  Web Admin API │          │  MiniApp API    │
│  (8000)        │          │  (8080)         │
└───────┬────────┘          └────────┬────────┘
        │                             │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │     Docker Network          │
        │   (redpacket_network)       │
        └──────────────┬──────────────┘
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
┌───▼────┐    ┌────────▼────────┐    ┌───▼──────┐
│PostgreSQL│   │    Frontend     │    │  Redis   │
│  (5432)  │   │    (3001)       │    │  (6379)  │
└─────────┘   └─────────────────┘    └──────────┘
```

---

## 6. 环境变量配置

### 6.1 后端环境变量

**来源**: `.env.production` 或 Docker Compose 环境变量

**关键变量**:
- `DATABASE_URL` - PostgreSQL 连接串
- `BOT_TOKEN` - Telegram Bot Token
- `MINIAPP_JWT_SECRET` - MiniApp JWT 密钥
- `ADMIN_SESSION_SECRET` - Web Admin 会话密钥

### 6.2 前端环境变量

**来源**: Docker Compose 环境变量或构建时注入

**关键变量**:
- `NEXT_PUBLIC_ADMIN_API_BASE_URL` - Web Admin API 基础地址
- `NEXT_PUBLIC_MINIAPP_API_BASE_URL` - MiniApp API 基础地址

**问题**: ⚠️ 当前默认值仍为 `localhost`，生产环境需要更新为公网 IP 或域名

### 6.3 测试环境变量

**来源**: PowerShell 脚本环境变量

**关键变量**:
- `API_TEST_ADMIN_BASE_URL` - 测试目标（Web Admin API）
- `API_TEST_MINIAPP_BASE_URL` - 测试目标（MiniApp API）

---

## 7. 健康检查配置

### 7.1 后端健康检查

| 服务 | 端点 | 检查间隔 | 状态 |
|------|------|---------|------|
| Web Admin API | `/healthz` | 30s | ✅ 已配置 |
| MiniApp API | `/healthz` | 30s | ✅ 已配置 |
| PostgreSQL | `pg_isready` | 10s | ✅ 已配置 |
| Redis | `redis-cli ping` | 10s | ✅ 已配置 |

### 7.2 前端健康检查

| 服务 | 端点 | 检查间隔 | 状态 |
|------|------|---------|------|
| Frontend | `http://localhost:3001` | 30s | ✅ 已配置 |

---

## 8. 现有部署脚本

### 8.1 Shell 脚本

| 脚本 | 位置 | 用途 | 状态 |
|------|------|------|------|
| `deploy.sh` | `deploy/scripts/deploy.sh` | 远程服务器部署 | ✅ 已存在 |
| `deploy_remote.sh` | `deploy/scripts/deploy_remote.sh` | 本地触发远程部署 | ✅ 已存在 |
| `auto_deploy_pipeline.sh` | `deploy/scripts/auto_deploy_pipeline.sh` | 自动化部署流水线 | ✅ 已存在 |

### 8.2 PowerShell 脚本

| 脚本 | 位置 | 用途 | 状态 |
|------|------|------|------|
| `run-full-stack-tests.ps1` | `docs/api-testing/run-full-stack-tests.ps1` | 全栈测试 | ✅ 已存在 |

**缺失**: ❌ 部署脚本（本地 + 生产）

---

## 9. CI/CD 现状

| CI/CD 系统 | 配置文件 | 状态 |
|-----------|---------|------|
| **GitHub Actions** | `.github/workflows/*.yml` | ❌ 缺失 |

---

## 10. 问题与改进建议

### 10.1 当前问题

1. ⚠️ **缺少统一的环境变量模板**（`.env.example`）
2. ⚠️ **前端 API 地址配置**（默认值仍为 `localhost`）
3. ⚠️ **缺少本地开发 Docker Compose 覆盖文件**（`docker-compose.override.yml`）
4. ⚠️ **缺少一键部署脚本**（本地 + 生产）
5. ⚠️ **缺少 CI/CD 配置**（GitHub Actions）
6. ⚠️ **缺少部署 + 测试一体化流程**

### 10.2 改进建议

1. ✅ 创建 `.env.example`, `.env.local.example`, `.env.production.example` 模板
2. ✅ 更新前端配置，使用环境变量而非硬编码
3. ✅ 创建 `docker-compose.override.yml` 用于本地开发
4. ✅ 创建 `docs/deployment/deploy-local.ps1` 和 `deploy-production.ps1`
5. ✅ 创建 `.github/workflows/ci-cd.yml` CI/CD 配置
6. ✅ 集成全栈测试到部署流程中

---

## 11. 下一步行动

### 优先级 1（必须）
1. ✅ 创建环境变量模板文件
2. ✅ 修复前端 API 地址配置
3. ✅ 创建本地开发 Docker Compose 覆盖文件
4. ✅ 创建部署脚本（本地 + 生产）

### 优先级 2（重要）
5. ✅ 创建 CI/CD 配置
6. ✅ 集成全栈测试到部署流程
7. ✅ 完善文档

---

**最后更新**: 2025-11-15

