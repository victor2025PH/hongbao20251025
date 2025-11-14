# 修复 redpacket_db 健康检查问题

> **问题**: `dependency failed to start: container redpacket_db is unhealthy`

---

## 🔍 问题分析

### 根本原因

1. **healthcheck 变量替换问题**: Docker Compose 的 healthcheck 在容器内执行，`${POSTGRES_USER:-redpacket}` 这种变量替换可能不工作
2. **POSTGRES_PASSWORD 未设置**: 如果 `.env.production` 中没有设置 `POSTGRES_PASSWORD`，容器无法启动
3. **PostgreSQL 15+ 兼容性**: healthcheck 需要适配 PostgreSQL 15+ 版本

---

## ✅ 已修复的问题

### 1. **docker-compose.production.yml** - 数据库配置

#### 修复前:
```yaml
environment:
  POSTGRES_USER: ${POSTGRES_USER:-redpacket}
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}  # ❌ 没有默认值
  POSTGRES_DB: ${POSTGRES_DB:-redpacket}
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-redpacket} -d ${POSTGRES_DB:-redpacket}"]  # ❌ 变量替换可能失败
```

#### 修复后:
```yaml
environment:
  POSTGRES_USER: ${POSTGRES_USER:-redpacket}
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-redpacket123}  # ✅ 添加默认值
  POSTGRES_DB: ${POSTGRES_DB:-redpacket}
healthcheck:
  # ✅ 使用容器内环境变量（自动可用）
  test: ["CMD-SHELL", "pg_isready -U \"$POSTGRES_USER\" -d \"$POSTGRES_DB\""]
```

### 2. **DATABASE_URL 配置**

#### 修复前:
```yaml
DATABASE_URL: ${DATABASE_URL:-postgresql+psycopg2://redpacket:${POSTGRES_PASSWORD}@db:5432/redpacket}
# ❌ 如果 POSTGRES_PASSWORD 未设置，会变成空字符串
```

#### 修复后:
```yaml
DATABASE_URL: ${DATABASE_URL:-postgresql+psycopg2://redpacket:${POSTGRES_PASSWORD:-redpacket123}@db:5432/redpacket}
# ✅ 添加默认密码
```

---

## 🚀 自动修复脚本

已创建自动修复脚本：`deploy/scripts/fix_db_healthcheck.sh`

### 使用方法:

```bash
# 在云主机上执行
cd /opt/redpacket
bash deploy/scripts/fix_db_healthcheck.sh
```

### 脚本功能:

1. ✅ 检查 `.env.production` 文件是否存在
2. ✅ 如果不存在，创建并设置默认值
3. ✅ 检查 `POSTGRES_PASSWORD` 是否设置
4. ✅ 如果未设置，添加默认密码（并提示修改）
5. ✅ 停止并删除现有数据库容器
6. ✅ 可选：删除数据库 volume（会丢失数据）
7. ✅ 启动数据库服务
8. ✅ 等待健康检查通过
9. ✅ 验证数据库连接

---

## 📝 手动修复步骤

如果不想使用脚本，可以手动修复：

### 步骤 1: 检查/创建 `.env.production` 文件

```bash
cd /opt/redpacket

# 如果文件不存在，创建它
cat > .env.production << 'EOF'
# PostgreSQL 数据库配置（必需）
POSTGRES_USER=redpacket
POSTGRES_PASSWORD=你的强密码  # ⚠️ 请修改为强密码！
POSTGRES_DB=redpacket

# 其他配置
FLAG_ENABLE_PUBLIC_GROUPS=1
DEBUG=false
TZ=Asia/Manila
EOF
```

### 步骤 2: 停止并重启数据库服务

```bash
# 停止数据库容器
docker compose -f docker-compose.production.yml stop db
docker compose -f docker-compose.production.yml rm -f db

# 如果数据库 volume 损坏，删除它（⚠️ 会丢失数据）
# docker volume rm redpacket_db_data

# 启动数据库服务
docker compose -f docker-compose.production.yml up -d db

# 查看日志
docker compose -f docker-compose.production.yml logs -f db
```

### 步骤 3: 验证健康检查

```bash
# 等待 30-60 秒后检查状态
docker compose -f docker-compose.production.yml ps db

# 应该显示 "healthy" 状态
```

### 步骤 4: 启动所有服务

```bash
docker compose -f docker-compose.production.yml up -d
```

---

## 🔍 验证 DATABASE_URL 格式

### 正确的格式:

```
postgresql+psycopg2://用户名:密码@主机:端口/数据库名
```

### 示例:

```
postgresql+psycopg2://redpacket:redpacket123@db:5432/redpacket
```

### 检查方法:

```bash
# 在 backend 容器中检查
docker compose -f docker-compose.production.yml exec web_admin env | grep DATABASE_URL

# 应该显示正确的连接字符串
```

---

## ⚠️ 重要提示

### 1. **密码安全**

- ⚠️ 默认密码 `redpacket123` 仅用于开发/测试
- ✅ 生产环境必须修改为强密码
- ✅ 修改后需要重启所有服务

### 2. **数据备份**

如果删除 volume，所有数据会丢失。建议先备份：

```bash
# 备份数据库
docker compose -f docker-compose.production.yml exec db pg_dump -U redpacket redpacket > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复数据库
docker compose -f docker-compose.production.yml exec -T db psql -U redpacket redpacket < backup_*.sql
```

### 3. **健康检查时间**

- `start_period: 30s` - 允许容器启动 30 秒
- `interval: 10s` - 每 10 秒检查一次
- `retries: 5` - 最多重试 5 次
- 总共最多等待: 30s + (10s × 5) = 80 秒

---

## 🐛 常见问题

### Q1: 健康检查一直失败

**可能原因**:
- `POSTGRES_PASSWORD` 未设置或为空
- 数据库 volume 损坏
- 端口被占用

**解决方法**:
```bash
# 1. 检查环境变量
docker compose -f docker-compose.production.yml config | grep POSTGRES_PASSWORD

# 2. 查看数据库日志
docker compose -f docker-compose.production.yml logs db

# 3. 检查端口占用
netstat -tuln | grep 5432
```

### Q2: DATABASE_URL 连接失败

**可能原因**:
- 密码不匹配
- 数据库未启动
- 网络问题

**解决方法**:
```bash
# 1. 验证数据库连接
docker compose -f docker-compose.production.yml exec db psql -U redpacket -d redpacket -c "SELECT 1;"

# 2. 检查 DATABASE_URL 格式
docker compose -f docker-compose.production.yml exec web_admin python -c "import os; print(os.getenv('DATABASE_URL'))"
```

### Q3: 容器启动后立即退出

**可能原因**:
- `POSTGRES_PASSWORD` 为空
- volume 权限问题

**解决方法**:
```bash
# 1. 检查日志
docker compose -f docker-compose.production.yml logs db

# 2. 检查 volume 权限
docker volume inspect redpacket_db_data
```

---

## ✅ 验证清单

修复完成后，请验证：

- [ ] `.env.production` 文件存在且包含 `POSTGRES_PASSWORD`
- [ ] `docker compose ps db` 显示状态为 `healthy`
- [ ] `docker compose logs db` 没有错误信息
- [ ] `docker compose exec db psql -U redpacket -d redpacket -c "SELECT 1;"` 成功
- [ ] `docker compose up -d` 所有服务启动成功
- [ ] `docker compose ps` 所有容器状态正常

---

*最后更新: 2025-01-XX*

