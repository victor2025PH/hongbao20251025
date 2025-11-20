# 📝 环境变量文件设置说明

## ⚠️ 重要提示

`.env`、`.env.local`、`.env.production` 等环境变量文件被 Git 全局忽略（符合安全最佳实践），需要**手动创建**。

---

## 🔧 创建环境变量文件

### 本地开发环境

```powershell
# 1. 复制模板（如果模板文件存在）
# 注意：由于 .env 文件被忽略，模板文件可能也无法直接创建
# 请参考 docs/deployment/ENV-CONFIG-GUIDE.md 中的模板内容

# 2. 手动创建 .env.local 文件
# 使用文本编辑器创建 .env.local，内容参考下方模板
```

**模板内容**（参考 `ENV-CONFIG-GUIDE.md` 中的详细说明）:

```bash
# 本地开发环境配置
BOT_TOKEN=你的_BOT_TOKEN
ADMIN_IDS=你的_管理员_ID

# 数据库（本地可以使用 SQLite 或 PostgreSQL）
DATABASE_URL=sqlite:///./data.sqlite
# 或
# DATABASE_URL=postgresql+psycopg2://redpacket:redpacket123@localhost:5432/redpacket

POSTGRES_USER=redpacket
POSTGRES_PASSWORD=redpacket123
POSTGRES_DB=redpacket

# 安全配置（本地开发可以使用简单值）
MINIAPP_JWT_SECRET=dev-secret-key
ADMIN_SESSION_SECRET=dev-session-secret
ADMIN_WEB_PASSWORD=admin123

# 前端配置（本地开发使用 localhost）
NEXT_PUBLIC_ADMIN_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_MINIAPP_API_BASE_URL=http://localhost:8080

# 测试配置
API_TEST_ADMIN_BASE_URL=http://localhost:8000
API_TEST_MINIAPP_BASE_URL=http://localhost:8080

DEBUG=true
```

### 生产环境

```powershell
# 在服务器上执行

# 1. 手动创建 .env.production 文件
# 使用文本编辑器创建 .env.production，内容参考下方模板

# 2. 设置文件权限（保护敏感信息）
chmod 600 .env.production
```

**模板内容**（参考 `ENV-CONFIG-GUIDE.md` 中的详细说明）:

```bash
# 生产环境配置
BOT_TOKEN=真实_BOT_TOKEN
ADMIN_IDS=真实_管理员_ID

# 数据库（生产环境必须使用 PostgreSQL）
POSTGRES_USER=redpacket
POSTGRES_PASSWORD=强密码_至少16位
POSTGRES_DB=redpacket

# 安全配置（生产环境必须使用强密钥）
# 生成密钥: openssl rand -hex 32
MINIAPP_JWT_SECRET=64位十六进制密钥
ADMIN_SESSION_SECRET=64位十六进制密钥
ADMIN_WEB_PASSWORD=强密码

# 前端配置（生产环境使用公网 IP 或域名）
NEXT_PUBLIC_ADMIN_API_BASE_URL=http://165.154.233.55:8000
# 或使用域名
# NEXT_PUBLIC_ADMIN_API_BASE_URL=https://api.yourdomain.com

NEXT_PUBLIC_MINIAPP_API_BASE_URL=http://165.154.233.55:8080
# 或使用域名
# NEXT_PUBLIC_MINIAPP_API_BASE_URL=https://miniapp-api.yourdomain.com

# 测试配置
API_TEST_ADMIN_BASE_URL=http://165.154.233.55:8000
API_TEST_MINIAPP_BASE_URL=http://165.154.233.55:8080

DEBUG=false
```

---

## 🔍 验证环境变量文件

### 本地开发环境

```powershell
# 检查文件是否存在
Test-Path .env.local

# 查看文件内容（不显示敏感值）
Get-Content .env.local | Select-String -Pattern "^(BOT_TOKEN|ADMIN_IDS|POSTGRES_PASSWORD|MINIAPP_JWT_SECRET|ADMIN_SESSION_SECRET|ADMIN_WEB_PASSWORD)=" | ForEach-Object { $_.Line -replace '=.*', '=***' }
```

### 生产环境

```bash
# 检查文件是否存在
test -f .env.production && echo "File exists" || echo "File not found"

# 查看文件权限
ls -la .env.production

# 应该显示: -rw-------（仅所有者可读写）
```

---

## 📚 相关文档

- [环境变量配置指南](ENV-CONFIG-GUIDE.md) - 详细的环境变量说明和示例
- [自动部署指南](README-AUTO-DEPLOY.md) - 一键部署说明

---

**最后更新**: 2025-11-15

