# 🔧 环境变量配置指南

## 📋 概述

本文档说明所有环境变量的含义、示例值和在哪个环境下生效。

---

## 🔑 核心配置变量

### BOT_TOKEN
- **说明**: Telegram Bot Token（从 @BotFather 获取）
- **类型**: 字符串
- **必填**: ✅ 是
- **示例**: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
- **生效环境**: 所有环境
- **来源**: `.env` / `.env.production`

### ADMIN_IDS
- **说明**: 管理员 Telegram ID（多个用逗号分隔）
- **类型**: 整数列表（逗号分隔）
- **必填**: ✅ 是
- **示例**: `123456789,987654321`
- **生效环境**: 所有环境
- **来源**: `.env` / `.env.production`

---

## 🗄️ 数据库配置变量

### DATABASE_URL
- **说明**: PostgreSQL 数据库连接字符串
- **类型**: 字符串（SQLAlchemy 格式）
- **必填**: ✅ 是
- **示例（Docker）**: `postgresql+psycopg2://redpacket:密码@db:5432/redpacket`
- **示例（本地 SQLite）**: `sqlite:///./data.sqlite`
- **生效环境**: 所有环境
- **来源**: `.env` / `.env.production`（或自动生成）

### POSTGRES_USER
- **说明**: PostgreSQL 数据库用户名
- **类型**: 字符串
- **必填**: ⚠️ 使用 PostgreSQL 时必填
- **默认值**: `redpacket`
- **生效环境**: 所有环境（使用 PostgreSQL 时）

### POSTGRES_PASSWORD
- **说明**: PostgreSQL 数据库密码
- **类型**: 字符串
- **必填**: ✅ 是（使用 PostgreSQL 时）
- **安全要求**: 至少 16 位，包含大小写字母、数字、特殊字符
- **生效环境**: 所有环境（使用 PostgreSQL 时）
- **⚠️ 需要人工填写**: 是

### POSTGRES_DB
- **说明**: PostgreSQL 数据库名称
- **类型**: 字符串
- **必填**: ⚠️ 使用 PostgreSQL 时必填
- **默认值**: `redpacket`
- **生效环境**: 所有环境（使用 PostgreSQL 时）

---

## 🔐 安全配置变量

### MINIAPP_JWT_SECRET
- **说明**: MiniApp JWT 密钥（用于生成和验证 JWT Token）
- **类型**: 字符串
- **必填**: ✅ 是
- **生成方式**: `openssl rand -hex 32`
- **示例**: `6d904bbb70db07852e96897d26effd92788c329aaf52bbb55df1ba2ecfe2bc2e`
- **生效环境**: 所有环境
- **⚠️ 需要人工填写**: 是（生产环境必须使用强密钥）

### ADMIN_SESSION_SECRET
- **说明**: Web Admin 会话密钥（用于加密 Session Cookie）
- **类型**: 字符串
- **必填**: ✅ 是
- **生成方式**: `openssl rand -hex 32`
- **示例**: `120a1ddb47366cb04d129923efd4d01d4721013dfdee2122cb6934a23e350d77`
- **生效环境**: 所有环境
- **⚠️ 需要人工填写**: 是（生产环境必须使用强密钥）

### ADMIN_WEB_PASSWORD
- **说明**: Web Admin 管理员密码
- **类型**: 字符串
- **必填**: ✅ 是
- **安全要求**: 至少 8 位，推荐包含大小写字母、数字、特殊字符
- **生效环境**: 所有环境
- **⚠️ 需要人工填写**: 是

---

## 🌐 前端 API 地址配置变量

### NEXT_PUBLIC_ADMIN_API_BASE_URL
- **说明**: Web Admin API 基础地址（供前端使用）
- **类型**: 字符串（URL）
- **必填**: ✅ 是（如果使用前端）
- **本地开发示例**: `http://localhost:8000`
- **Docker 示例**: `http://web_admin:8000`（容器间通信）
- **生产示例**: `http://165.154.233.55:8000` 或 `https://api.yourdomain.com`
- **生效环境**: 前端构建时注入
- **⚠️ 需要人工填写**: 生产环境是

### NEXT_PUBLIC_MINIAPP_API_BASE_URL
- **说明**: MiniApp API 基础地址（供前端使用）
- **类型**: 字符串（URL）
- **必填**: ✅ 是（如果使用前端）
- **本地开发示例**: `http://localhost:8080`
- **Docker 示例**: `http://miniapp_api:8080`（容器间通信）
- **生产示例**: `http://165.154.233.55:8080` 或 `https://miniapp-api.yourdomain.com`
- **生效环境**: 前端构建时注入
- **⚠️ 需要人工填写**: 生产环境是

---

## 🧪 测试配置变量

### API_TEST_ADMIN_BASE_URL
- **说明**: 测试目标地址（Web Admin API）
- **类型**: 字符串（URL）
- **必填**: ❌ 否（有默认值）
- **默认值**: `http://165.154.233.55:8000`
- **本地测试示例**: `http://localhost:8000`
- **生产测试示例**: `http://165.154.233.55:8000`
- **生效环境**: 测试脚本运行时

### API_TEST_MINIAPP_BASE_URL
- **说明**: 测试目标地址（MiniApp API）
- **类型**: 字符串（URL）
- **必填**: ❌ 否（有默认值）
- **默认值**: `http://165.154.233.55:8080`
- **本地测试示例**: `http://localhost:8080`
- **生产测试示例**: `http://165.154.233.55:8080`
- **生效环境**: 测试脚本运行时

---

## 📝 需要人工填写的敏感值

### 必填项（生产环境）

| 变量名 | 说明 | 生成方式 |
|-------|------|---------|
| `BOT_TOKEN` | Telegram Bot Token | 从 @BotFather 获取 |
| `ADMIN_IDS` | 管理员 Telegram ID | 从 Telegram 获取 |
| `POSTGRES_PASSWORD` | 数据库密码 | 手动设置（至少 16 位） |
| `MINIAPP_JWT_SECRET` | JWT 密钥 | `openssl rand -hex 32` |
| `ADMIN_SESSION_SECRET` | 会话密钥 | `openssl rand -hex 32` |
| `ADMIN_WEB_PASSWORD` | Web 管理员密码 | 手动设置（至少 8 位） |
| `NEXT_PUBLIC_ADMIN_API_BASE_URL` | 前端 Admin API 地址 | 根据部署环境设置 |
| `NEXT_PUBLIC_MINIAPP_API_BASE_URL` | 前端 MiniApp API 地址 | 根据部署环境设置 |

### 可选项（根据需求）

| 变量名 | 说明 |
|-------|------|
| `REDIS_PASSWORD` | Redis 密码（如果启用 Redis） |
| `REDIS_URL` | Redis 连接 URL（如果启用 Redis） |
| `NOWPAYMENTS_API_KEY` | NowPayments API 密钥（如果使用充值功能） |
| `NOWPAYMENTS_IPN_SECRET` | NowPayments IPN 密钥（如果使用充值功能） |
| `OPENAI_API_KEY` | OpenAI API 密钥（如果使用 AI 功能） |

---

## 🌍 环境特定配置

### 本地开发环境 (`.env.local`)

```bash
# 使用 SQLite（无需 Docker）
DATABASE_URL=sqlite:///./data.sqlite

# 或使用本地 PostgreSQL
DATABASE_URL=postgresql+psycopg2://redpacket:redpacket123@localhost:5432/redpacket

# 前端使用 localhost
NEXT_PUBLIC_ADMIN_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_MINIAPP_API_BASE_URL=http://localhost:8080

# 启用调试
DEBUG=true
NEXT_PUBLIC_ENABLE_DEVTOOLS=true
```

### Docker 开发环境 (`docker-compose.yml`)

```bash
# 使用 Docker 服务名
DATABASE_URL=postgresql+psycopg2://redpacket:密码@db:5432/redpacket

# 前端使用容器名（构建时）或 localhost（运行时访问）
NEXT_PUBLIC_ADMIN_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_MINIAPP_API_BASE_URL=http://localhost:8080
```

### 生产环境 (`.env.production`)

```bash
# 使用 Docker 服务名（容器间通信）
DATABASE_URL=postgresql+psycopg2://redpacket:强密码@db:5432/redpacket

# 前端使用公网 IP 或域名
NEXT_PUBLIC_ADMIN_API_BASE_URL=https://api.yourdomain.com
NEXT_PUBLIC_MINIAPP_API_BASE_URL=https://miniapp-api.yourdomain.com

# 禁用调试
DEBUG=false
NEXT_PUBLIC_ENABLE_DEVTOOLS=false
```

---

## 📚 配置文件优先级

### Docker Compose 环境变量优先级

1. **环境变量** (`environment:` 字段)
2. **`.env.production`** 或 **`.env`** 文件 (`env_file:` 字段)
3. **默认值** (`${VAR:-default}` 语法)

### Next.js 前端环境变量

- **构建时注入**: 通过 `next.config.ts` 的 `env` 字段或 Docker 构建参数
- **运行时读取**: Next.js 公共变量（`NEXT_PUBLIC_*`）在构建时注入，无法运行时修改

---

## 🔒 安全注意事项

1. **不要提交敏感文件**: 
   - ❌ 不要将 `.env`、`.env.production`、`.env.local` 提交到 Git
   - ✅ 只提交 `.env.example`、`.env.local.example`、`.env.production.example`

2. **生产环境密钥**:
   - 使用强随机密钥（`openssl rand -hex 32`）
   - 定期轮换密钥
   - 使用密钥管理服务（如 AWS Secrets Manager、HashiCorp Vault）

3. **数据库密码**:
   - 至少 16 位
   - 包含大小写字母、数字、特殊字符
   - 不要使用默认密码

---

## 📖 相关文档

- [部署现状分析](DEPLOYMENT-CURRENT-STATE.md) - 当前部署架构
- [自动部署指南](README-AUTO-DEPLOY.md) - 一键部署说明

---

**最后更新**: 2025-11-15

