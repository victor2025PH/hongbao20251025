# 🧪 部署测试与验证完整流程

> **当前状态**: 数据库修复成功，`redpacket_db` 已通过健康检查  
> **下一步**: 启动所有服务并进行完整测试

---

## 📊 当前状态检查

### 步骤 1: 检查当前服务状态

```bash
cd /opt/redpacket

# 查看所有服务状态
docker compose -f docker-compose.production.yml ps
```

**预期结果**:
- ✅ `redpacket_db` - `healthy` (已修复)
- ⚠️ 其他服务可能显示 `unhealthy` 或 `Restarting`（这是正常的，需要启动所有服务）

---

## 🚀 完整部署流程

### 步骤 2: 启动所有服务

```bash
# 启动所有服务（后台运行）
docker compose -f docker-compose.production.yml up -d

# 等待 30-60 秒让所有服务启动
echo "等待服务启动..."
sleep 30
```

### 步骤 3: 检查所有服务状态

```bash
# 再次检查服务状态
docker compose -f docker-compose.production.yml ps
```

**预期结果**: 所有服务应该显示 `healthy` 或 `running`

如果某些服务还是 `unhealthy`，继续执行下面的测试步骤来定位问题。

---

## 🔍 服务测试流程

### 测试 1: 数据库服务测试

```bash
# 1.1 检查数据库容器状态
docker compose -f docker-compose.production.yml ps db

# 1.2 测试数据库连接
docker compose -f docker-compose.production.yml exec db psql -U redpacket -d redpacket -c "SELECT version();"

# 1.3 检查数据库表是否存在（如果是首次部署，需要初始化）
docker compose -f docker-compose.production.yml exec db psql -U redpacket -d redpacket -c "\dt"

# 预期输出: 应该显示数据库表列表，或者提示 "Did not find any relations"
```

**如果表不存在，需要初始化数据库**:
```bash
docker compose -f docker-compose.production.yml exec web_admin python -c "from models.db import init_db; init_db()"
```

---

### 测试 2: Web Admin 服务测试

```bash
# 2.1 检查 Web Admin 容器状态
docker compose -f docker-compose.production.yml ps web_admin

# 2.2 测试健康检查端点
curl -v http://127.0.0.1:8000/healthz

# 预期输出: HTTP/1.1 200 OK

# 2.3 测试就绪检查端点
curl -v http://127.0.0.1:8000/readyz

# 预期输出: HTTP/1.1 200 OK

# 2.4 测试指标端点
curl http://127.0.0.1:8000/metrics | head -20

# 预期输出: Prometheus 格式的指标数据

# 2.5 检查 Web Admin 日志
docker compose -f docker-compose.production.yml logs web_admin --tail 50
```

**如果健康检查失败，查看日志找出原因**:
```bash
docker compose -f docker-compose.production.yml logs web_admin --tail 100
```

---

### 测试 3: MiniApp API 服务测试

```bash
# 3.1 检查 MiniApp API 容器状态
docker compose -f docker-compose.production.yml ps miniapp_api

# 3.2 测试健康检查端点
curl -v http://127.0.0.1:8080/healthz

# 预期输出: HTTP/1.1 200 OK

# 3.3 测试就绪检查端点
curl -v http://127.0.0.1:8080/readyz

# 预期输出: HTTP/1.1 200 OK

# 3.4 检查 MiniApp API 日志
docker compose -f docker-compose.production.yml logs miniapp_api --tail 50
```

---

### 测试 4: Telegram Bot 服务测试

```bash
# 4.1 检查 Bot 容器状态
docker compose -f docker-compose.production.yml ps bot

# 4.2 检查 Bot 日志（查看是否有连接错误）
docker compose -f docker-compose.production.yml logs bot --tail 100

# 预期输出: 应该看到 Bot 启动信息和 "Bot started" 或类似消息

# 4.3 测试 Bot 是否响应（在 Telegram 中发送 /start 命令）
# 注意: 这需要在 Telegram 客户端中测试
```

**常见问题**:
- 如果看到 "Unauthorized" 错误，检查 `BOT_TOKEN` 是否正确
- 如果看到连接错误，检查网络连接和防火墙设置

---

### 测试 5: Frontend 服务测试

```bash
# 5.1 检查 Frontend 容器状态
docker compose -f docker-compose.production.yml ps frontend

# 5.2 测试前端服务
curl -I http://127.0.0.1:3001

# 预期输出: HTTP/1.1 200 OK

# 5.3 检查前端日志
docker compose -f docker-compose.production.yml logs frontend --tail 50
```

---

### 测试 6: Redis 服务测试（可选）

```bash
# 6.1 检查 Redis 容器状态
docker compose -f docker-compose.production.yml ps redis

# 6.2 测试 Redis 连接
docker compose -f docker-compose.production.yml exec redis redis-cli ping

# 预期输出: PONG
```

---

## 🎯 功能测试流程

### 功能测试 1: Web Admin 登录测试

```bash
# 1. 在浏览器中访问（如果配置了 Nginx 反向代理）
# http://你的域名/admin
# 或直接访问
# http://165.154.233.55:8000/admin

# 2. 使用 .env.production 中配置的账号密码登录
# ADMIN_WEB_USER=admin
# ADMIN_WEB_PASSWORD=你的密码

# 3. 测试功能:
# - 登录页面是否正常显示
# - 登录是否成功
# - 仪表板是否正常显示
# - 各个菜单是否可访问
```

**如果无法访问，检查**:
```bash
# 检查端口是否开放
sudo netstat -tuln | grep 8000

# 检查防火墙设置
sudo ufw status

# 如果需要开放端口（不推荐，建议使用 Nginx 反向代理）
sudo ufw allow 8000/tcp
```

---

### 功能测试 2: MiniApp API 测试

```bash
# 1. 测试公开 API 端点
curl http://127.0.0.1:8080/healthz

# 2. 测试认证端点（需要 Token）
curl -X POST http://127.0.0.1:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'

# 预期输出: 根据配置返回 Token 或错误信息
```

---

### 功能测试 3: Telegram Bot 功能测试

**在 Telegram 客户端中测试**:

1. 找到你的 Bot（通过 @BotFather 获取 Bot 用户名）
2. 发送 `/start` 命令
3. 测试主要功能:
   - 菜单导航
   - 红包功能
   - 充值功能
   - 其他功能

**如果 Bot 不响应，检查日志**:
```bash
docker compose -f docker-compose.production.yml logs bot -f
```

---

## 📋 完整验证清单

### 基础设施验证

- [ ] 所有 Docker 容器正常运行
- [ ] 数据库健康检查通过
- [ ] Redis 服务正常（如果使用）
- [ ] 网络连接正常

### 服务健康检查

- [ ] Web Admin `/healthz` 返回 200
- [ ] Web Admin `/readyz` 返回 200
- [ ] MiniApp API `/healthz` 返回 200
- [ ] MiniApp API `/readyz` 返回 200
- [ ] Frontend 服务可访问

### 数据库验证

- [ ] 数据库连接成功
- [ ] 数据库表已创建（或已初始化）
- [ ] 可以执行 SQL 查询

### 功能验证

- [ ] Web Admin 可以登录
- [ ] Web Admin 仪表板正常显示
- [ ] Telegram Bot 响应命令
- [ ] MiniApp API 可以访问
- [ ] Frontend 页面正常显示

---

## 🐛 常见问题排查

### 问题 1: 服务显示 unhealthy

**排查步骤**:
```bash
# 1. 查看服务日志
docker compose -f docker-compose.production.yml logs [服务名] --tail 100

# 2. 检查环境变量
docker compose -f docker-compose.production.yml exec [服务名] env | grep -E "DATABASE_URL|BOT_TOKEN"

# 3. 手动测试健康检查
docker compose -f docker-compose.production.yml exec [服务名] curl http://localhost:8000/healthz
```

**常见原因**:
- 环境变量未设置或错误
- 数据库连接失败
- 端口冲突
- 依赖服务未启动

---

### 问题 2: 数据库连接失败

**排查步骤**:
```bash
# 1. 检查 DATABASE_URL 环境变量
docker compose -f docker-compose.production.yml exec web_admin env | grep DATABASE_URL

# 2. 测试数据库连接
docker compose -f docker-compose.production.yml exec web_admin python -c "
from models.db import engine
try:
    conn = engine.connect()
    print('✅ 数据库连接成功')
    conn.close()
except Exception as e:
    print(f'❌ 数据库连接失败: {e}')
"

# 3. 检查数据库服务是否运行
docker compose -f docker-compose.production.yml ps db
```

**解决方案**:
- 确保 `POSTGRES_PASSWORD` 在 `.env.production` 中正确设置
- 确保 `DATABASE_URL` 格式正确
- 确保数据库容器已启动并通过健康检查

---

### 问题 3: Bot Token 错误

**排查步骤**:
```bash
# 1. 检查 BOT_TOKEN 环境变量
docker compose -f docker-compose.production.yml exec bot env | grep BOT_TOKEN

# 2. 查看 Bot 日志
docker compose -f docker-compose.production.yml logs bot --tail 50 | grep -i "token\|unauthorized\|error"
```

**解决方案**:
- 确保 `.env.production` 中 `BOT_TOKEN` 正确设置
- 从 @BotFather 获取正确的 Token
- 重启 Bot 服务: `docker compose -f docker-compose.production.yml restart bot`

---

### 问题 4: 端口被占用

**排查步骤**:
```bash
# 检查端口占用
sudo netstat -tuln | grep -E "5432|8000|8080|3001"

# 查看哪个进程占用端口
sudo lsof -i :8000
```

**解决方案**:
- 停止占用端口的服务
- 或修改 `docker-compose.production.yml` 中的端口映射

---

## 🔄 下一步操作

### 1. 配置 Nginx 反向代理（推荐）

如果需要通过域名访问服务，配置 Nginx:

```bash
# 创建 Nginx 配置
sudo nano /etc/nginx/sites-available/redpacket

# 配置内容（示例）:
server {
    listen 80;
    server_name 你的域名.com;

    # Web Admin
    location /admin {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # MiniApp API
    location /api {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# 启用配置
sudo ln -s /etc/nginx/sites-available/redpacket /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

### 2. 配置 SSL 证书（HTTPS）

```bash
# 安装 Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# 获取 SSL 证书
sudo certbot --nginx -d 你的域名.com

# 自动续期
sudo certbot renew --dry-run
```

---

### 3. 设置自动备份

```bash
# 创建备份脚本
cat > /opt/redpacket/backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/redpacket/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
docker compose -f /opt/redpacket/docker-compose.production.yml exec -T db pg_dump -U redpacket redpacket > $BACKUP_DIR/backup_$DATE.sql
# 保留最近 7 天的备份
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
EOF

chmod +x /opt/redpacket/backup_db.sh

# 添加到 crontab（每天凌晨 2 点备份）
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/redpacket/backup_db.sh") | crontab -
```

---

### 4. 监控和日志管理

```bash
# 查看所有服务日志
docker compose -f docker-compose.production.yml logs -f

# 查看特定服务日志
docker compose -f docker-compose.production.yml logs -f web_admin

# 查看最近 100 行日志
docker compose -f docker-compose.production.yml logs --tail 100
```

---

### 5. 性能优化

```bash
# 检查资源使用情况
docker stats

# 检查磁盘使用
df -h

# 清理未使用的 Docker 资源
docker system prune -a
```

---

## 📊 一键测试脚本

创建完整的测试脚本:

```bash
cat > /opt/redpacket/test_all_services.sh << 'EOF'
#!/bin/bash
echo "🧪 开始测试所有服务..."
echo ""

# 1. 检查服务状态
echo "📊 1. 检查服务状态..."
docker compose -f docker-compose.production.yml ps
echo ""

# 2. 测试数据库
echo "🗄️  2. 测试数据库..."
docker compose -f docker-compose.production.yml exec db psql -U redpacket -d redpacket -c "SELECT version();" && echo "✅ 数据库连接成功" || echo "❌ 数据库连接失败"
echo ""

# 3. 测试 Web Admin
echo "🌐 3. 测试 Web Admin..."
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://127.0.0.1:8000/healthz
echo ""

# 4. 测试 MiniApp API
echo "📱 4. 测试 MiniApp API..."
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://127.0.0.1:8080/healthz
echo ""

# 5. 测试 Frontend
echo "💻 5. 测试 Frontend..."
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://127.0.0.1:3001
echo ""

# 6. 测试 Redis
echo "🔴 6. 测试 Redis..."
docker compose -f docker-compose.production.yml exec redis redis-cli ping && echo "✅ Redis 连接成功" || echo "❌ Redis 连接失败"
echo ""

echo "✅ 测试完成！"
EOF

chmod +x /opt/redpacket/test_all_services.sh

# 执行测试
/opt/redpacket/test_all_services.sh
```

---

## ✅ 部署成功确认

如果所有测试都通过，你的部署就成功了！🎉

**成功标志**:
- ✅ 所有服务状态为 `healthy` 或 `running`
- ✅ 所有健康检查端点返回 200
- ✅ 数据库连接正常
- ✅ Web Admin 可以登录
- ✅ Telegram Bot 响应命令
- ✅ 前端页面正常显示

---

## 📞 需要帮助？

如果遇到问题:
1. 查看服务日志: `docker compose -f docker-compose.production.yml logs -f [服务名]`
2. 查看测试文档: `cat TEST_AND_VERIFY.md`
3. 查看部署文档: `cat DEPLOY_NEXT_STEPS.md`
4. 查看修复文档: `cat FIX_DB_HEALTHCHECK.md`

---

*最后更新: 2025-01-XX*

