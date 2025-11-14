# 🚀 云服务器部署操作指南

> **当前状态**: 数据库健康检查问题已修复，代码已推送到 GitHub  
> **下一步**: 在云服务器上执行部署

---

## 📋 部署前准备

### 1. 确认云服务器信息

根据你的配置，你有两台服务器：
- **马尼拉**: `165.154.233.55`
- **洛杉矶**: `165.154.254.99`

**用户名**: `ubuntu`  
**密码**: `Along2025!!!`

### 2. 确认项目目录

项目应该部署在 `/opt/redpacket` 目录（或你之前配置的目录）

---

## 🔧 部署步骤（按顺序执行）

### 步骤 1: 连接到云服务器

```bash
# 选择一台服务器（建议先在马尼拉测试）
ssh ubuntu@165.154.233.55
# 输入密码: Along2025!!!
```

### 步骤 2: 进入项目目录并拉取最新代码

```bash
# 进入项目目录
cd /opt/redpacket

# 检查当前状态
git status

# 拉取最新代码（包含数据库修复）
git pull origin master

# 确认已更新
git log --oneline -5
```

**预期输出**: 应该看到最新的 commit `Fix redpacket_db healthcheck and POSTGRES_PASSWORD configuration`

---

### 步骤 3: 检查/创建 `.env.production` 文件

```bash
# 检查文件是否存在
ls -la .env.production

# 如果文件不存在，创建它
cat > .env.production << 'EOF'
# PostgreSQL 数据库配置（必需）
POSTGRES_USER=redpacket
POSTGRES_PASSWORD=你的强密码  # ⚠️ 请修改为强密码！
POSTGRES_DB=redpacket

# 数据库连接 URL（可选，会自动生成）
# DATABASE_URL=postgresql+psycopg2://redpacket:你的密码@db:5432/redpacket

# Telegram Bot 配置（必需）
BOT_TOKEN=你的BotToken

# 管理员配置
ADMIN_IDS=你的Telegram用户ID
SUPER_ADMINS=你的Telegram用户ID

# 其他配置
FLAG_ENABLE_PUBLIC_GROUPS=1
DEBUG=false
TZ=Asia/Manila

# Web Admin 配置
ADMIN_WEB_USER=admin
ADMIN_WEB_PASSWORD=你的管理员密码
ADMIN_SESSION_SECRET=change_me_at_least_32_chars_random_string

# MiniApp 配置
MINIAPP_JWT_SECRET=change_me_to_secure_value
MINIAPP_JWT_ISSUER=miniapp
MINIAPP_JWT_EXPIRE_SECONDS=7200

# NOWPayments 配置（如果使用）
NOWPAYMENTS_API_KEY=你的API密钥
NOWPAYMENTS_IPN_SECRET=你的IPN密钥
NOWPAYMENTS_IPN_URL=https://你的域名/api/v1/ipn/nowpayments
EOF

# 编辑文件（修改密码和其他配置）
nano .env.production
```

**重要提示**:
- ⚠️ **必须修改 `POSTGRES_PASSWORD` 为强密码**
- ⚠️ **必须填写 `BOT_TOKEN`**
- ⚠️ **必须填写 `ADMIN_IDS`**（你的 Telegram 用户 ID）

---

### 步骤 4: 执行数据库修复脚本

```bash
# 给脚本添加执行权限
chmod +x deploy/scripts/fix_db_healthcheck.sh

# 执行修复脚本
bash deploy/scripts/fix_db_healthcheck.sh
```

**脚本会执行以下操作**:
1. ✅ 检查 `.env.production` 文件
2. ✅ 验证 `POSTGRES_PASSWORD` 是否设置
3. ✅ 停止并删除现有数据库容器
4. ✅ 询问是否删除数据库 volume（⚠️ 会丢失数据）
5. ✅ 启动数据库服务
6. ✅ 等待健康检查通过（最多 60 秒）
7. ✅ 验证数据库连接

**预期输出**:
```
✅ 数据库健康检查通过！
✅ 数据库连接成功！
```

---

### 步骤 5: 验证数据库服务

```bash
# 检查数据库容器状态
docker compose -f docker-compose.production.yml ps db

# 应该显示: healthy

# 查看数据库日志（可选）
docker compose -f docker-compose.production.yml logs db --tail 50

# 测试数据库连接
docker compose -f docker-compose.production.yml exec db psql -U redpacket -d redpacket -c "SELECT version();"
```

---

### 步骤 6: 启动所有服务

```bash
# 启动所有服务（后台运行）
docker compose -f docker-compose.production.yml up -d

# 查看所有服务状态
docker compose -f docker-compose.production.yml ps
```

**预期输出**: 所有服务应该显示 `healthy` 或 `running` 状态

---

### 步骤 7: 等待服务启动并验证

```bash
# 等待 30-60 秒让所有服务启动
sleep 30

# 再次检查所有服务状态
docker compose -f docker-compose.production.yml ps

# 查看所有服务日志（实时）
docker compose -f docker-compose.production.yml logs -f
```

**按 `Ctrl+C` 退出日志查看**

---

### 步骤 8: 验证各个服务

```bash
# 1. 验证数据库
docker compose -f docker-compose.production.yml exec db psql -U redpacket -d redpacket -c "SELECT 1;"

# 2. 验证 Web Admin (端口 8000)
curl http://127.0.0.1:8000/healthz
curl http://127.0.0.1:8000/readyz

# 3. 验证 MiniApp API (端口 8080)
curl http://127.0.0.1:8080/healthz
curl http://127.0.0.1:8080/readyz

# 4. 验证前端 (端口 3001)
curl http://127.0.0.1:3001 | head -20
```

---

### 步骤 9: 初始化数据库（如果是首次部署）

```bash
# 进入 backend 容器执行数据库初始化
docker compose -f docker-compose.production.yml exec web_admin python -c "from models.db import init_db; init_db()"
```

---

### 步骤 10: 配置 Nginx 反向代理（如果需要）

如果你需要通过域名访问服务，需要配置 Nginx：

```bash
# 编辑 Nginx 配置
sudo nano /etc/nginx/sites-available/redpacket

# 示例配置内容：
server {
    listen 80;
    server_name 你的域名.com;

    # Web Admin
    location /admin {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # MiniApp API
    location /api {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Frontend
    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# 启用配置
sudo ln -s /etc/nginx/sites-available/redpacket /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔍 故障排查

### 问题 1: 数据库健康检查失败

```bash
# 查看数据库日志
docker compose -f docker-compose.production.yml logs db

# 检查环境变量
docker compose -f docker-compose.production.yml config | grep POSTGRES_PASSWORD

# 手动测试健康检查
docker compose -f docker-compose.production.yml exec db pg_isready -U redpacket -d redpacket
```

**解决方案**:
- 确保 `.env.production` 中 `POSTGRES_PASSWORD` 已设置且不为空
- 如果 volume 损坏，删除并重建：`docker volume rm redpacket_db_data`

---

### 问题 2: 服务无法连接到数据库

```bash
# 检查 DATABASE_URL 环境变量
docker compose -f docker-compose.production.yml exec web_admin env | grep DATABASE_URL

# 测试数据库连接
docker compose -f docker-compose.production.yml exec web_admin python -c "from models.db import engine; print(engine.connect())"
```

**解决方案**:
- 确保 `POSTGRES_PASSWORD` 在 `.env.production` 中设置
- 确保 `DATABASE_URL` 格式正确：`postgresql+psycopg2://redpacket:密码@db:5432/redpacket`

---

### 问题 3: 容器启动后立即退出

```bash
# 查看容器日志
docker compose -f docker-compose.production.yml logs --tail 100

# 检查容器状态
docker compose -f docker-compose.production.yml ps -a
```

**解决方案**:
- 检查 `.env.production` 中必需的环境变量是否都已设置
- 查看具体服务的日志找出错误原因

---

### 问题 4: 端口被占用

```bash
# 检查端口占用
sudo netstat -tuln | grep -E '5432|8000|8080|3001'

# 如果端口被占用，停止占用端口的服务或修改 docker-compose.production.yml 中的端口映射
```

---

## 📊 部署验证清单

部署完成后，请验证以下项目：

- [ ] `docker compose ps` 所有服务状态为 `healthy` 或 `running`
- [ ] 数据库健康检查通过：`docker compose exec db pg_isready -U redpacket -d redpacket`
- [ ] Web Admin 健康检查通过：`curl http://127.0.0.1:8000/healthz`
- [ ] MiniApp API 健康检查通过：`curl http://127.0.0.1:8080/healthz`
- [ ] 前端服务可访问：`curl http://127.0.0.1:3001 | head -20`
- [ ] 数据库连接正常：`docker compose exec db psql -U redpacket -d redpacket -c "SELECT 1;"`
- [ ] 所有服务日志无错误：`docker compose logs --tail 50`

---

## 🔄 日常维护命令

### 查看服务状态

```bash
docker compose -f docker-compose.production.yml ps
```

### 查看服务日志

```bash
# 查看所有服务日志
docker compose -f docker-compose.production.yml logs -f

# 查看特定服务日志
docker compose -f docker-compose.production.yml logs -f db
docker compose -f docker-compose.production.yml logs -f web_admin
docker compose -f docker-compose.production.yml logs -f bot
```

### 重启服务

```bash
# 重启所有服务
docker compose -f docker-compose.production.yml restart

# 重启特定服务
docker compose -f docker-compose.production.yml restart db
docker compose -f docker-compose.production.yml restart web_admin
```

### 更新代码并重新部署

```bash
# 1. 拉取最新代码
cd /opt/redpacket
git pull origin master

# 2. 重新构建并启动服务
docker compose -f docker-compose.production.yml up -d --build

# 3. 查看日志确认无错误
docker compose -f docker-compose.production.yml logs -f
```

### 备份数据库

```bash
# 创建备份
docker compose -f docker-compose.production.yml exec db pg_dump -U redpacket redpacket > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复备份
docker compose -f docker-compose.production.yml exec -T db psql -U redpacket redpacket < backup_*.sql
```

---

## 🎯 快速部署命令（一键执行）

如果你已经配置好 `.env.production`，可以使用以下命令快速部署：

```bash
#!/bin/bash
# 快速部署脚本

cd /opt/redpacket

# 1. 拉取最新代码
echo "📥 拉取最新代码..."
git pull origin master

# 2. 执行数据库修复
echo "🔧 修复数据库配置..."
bash deploy/scripts/fix_db_healthcheck.sh

# 3. 启动所有服务
echo "🚀 启动所有服务..."
docker compose -f docker-compose.production.yml up -d

# 4. 等待服务启动
echo "⏳ 等待服务启动（30秒）..."
sleep 30

# 5. 检查服务状态
echo "📊 检查服务状态..."
docker compose -f docker-compose.production.yml ps

echo "✅ 部署完成！"
```

保存为 `deploy.sh` 并执行：

```bash
chmod +x deploy.sh
./deploy.sh
```

---

## 📞 需要帮助？

如果遇到问题，请：

1. **查看日志**: `docker compose -f docker-compose.production.yml logs -f`
2. **检查服务状态**: `docker compose -f docker-compose.production.yml ps`
3. **查看修复文档**: `cat FIX_DB_HEALTHCHECK.md`
4. **查看总结报告**: `cat DB_FIX_SUMMARY.md`

---

*最后更新: 2025-01-XX*

