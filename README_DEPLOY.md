# 生产环境部署文档

本文档提供 037 红包系统管理后台的生产环境完整部署方案，包括 Docker、Nginx、监控等配置。

> **参考文档**: 
> - 架构说明: `037_ARCHITECTURE.md`
> - 部署指南: `037_DEPLOY_GUIDE.md`
> - API 对照表: `037_API_TABLE.md`

---

## 目录

- [部署架构](#部署架构)
- [前置要求](#前置要求)
- [快速开始](#快速开始)
- [详细部署步骤](#详细部署步骤)
- [监控与日志](#监控与日志)
- [维护与更新](#维护与更新)
- [故障排查](#故障排查)

---

## 部署架构

### 服务组件

| 服务 | 端口（内部） | 端口（外部） | 说明 |
|------|-------------|-------------|------|
| **PostgreSQL** | 5432 | 127.0.0.1:5432 | 数据库 |
| **Redis** | 6379 | 127.0.0.1:6379 | 缓存（可选） |
| **Telegram Bot** | - | - | Bot 服务 |
| **Web Admin** | 8000 | 127.0.0.1:8000 | Web 管理后台 |
| **MiniApp API** | 8080 | 127.0.0.1:8080 | MiniApp 后端 API |
| **前端控制台** | 3001 | 127.0.0.1:3001 | Next.js 前端 |
| **Prometheus** | 9090 | 127.0.0.1:9090 | 监控指标收集 |
| **Grafana** | 3000 | 127.0.0.1:3000 | 监控可视化 |
| **Nginx** | 80, 443 | 80, 443 | 反向代理和 HTTPS |

### 网络架构

```
                    ┌─────────────────┐
                    │   Internet      │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │     Nginx       │
                    │  (HTTPS 443)    │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                      │
  ┌─────▼─────┐      ┌──────▼──────┐      ┌───────▼──────┐
  │  Frontend │      │  Web Admin  │      │  MiniApp API │
  │   :3001   │      │    :8000    │      │    :8080     │
  └───────────┘      └──────┬──────┘      └──────┬──────┘
                             │                     │
                             └──────────┬──────────┘
                                        │
                              ┌─────────▼─────────┐
                              │   PostgreSQL      │
                              │      :5432        │
                              └───────────────────┘
```

---

## 前置要求

### 服务器要求

- **操作系统**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **CPU**: 2 核心以上
- **内存**: 4GB 以上（推荐 8GB）
- **磁盘**: 50GB 以上（推荐 100GB）
- **网络**: 公网 IP，开放 80、443 端口

### 软件要求

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Nginx**: 1.18+
- **Certbot**: 用于 Let's Encrypt SSL 证书

### 域名与 SSL

- 已配置域名（如 `yourdomain.com`）
- DNS A 记录指向服务器 IP
- 准备申请 Let's Encrypt SSL 证书

---

## 快速开始

### 1. 克隆代码并准备环境

```bash
# 克隆代码（或上传代码到服务器）
git clone <repository-url>
cd 037重新开发新功能

# 创建必要的目录
mkdir -p logs backups deploy/prometheus deploy/grafana/dashboards deploy/grafana/datasources
```

### 2. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.production.example .env.production

# 编辑环境变量（填入真实值）
nano .env.production
```

**必填项**:
- `BOT_TOKEN`: Telegram Bot Token
- `DATABASE_URL`: PostgreSQL 连接串
- `POSTGRES_PASSWORD`: 数据库密码（强密码）
- `MINIAPP_JWT_SECRET`: JWT 密钥（强随机字符串）
- `ADMIN_SESSION_SECRET`: 会话密钥（强随机字符串）
- `ADMIN_IDS`: 管理员 Telegram ID（逗号分隔）

### 3. 构建 Docker 镜像

```bash
# 构建后端镜像
docker build -f Dockerfile.backend -t redpacket/backend:latest .

# 构建前端镜像
docker build -f frontend-next/Dockerfile -t redpacket/frontend:latest ./frontend-next
```

### 4. 启动服务

```bash
# 使用 Docker Compose 启动所有服务
docker-compose -f docker-compose.production.yml up -d

# 查看服务状态
docker-compose -f docker-compose.production.yml ps

# 查看日志
docker-compose -f docker-compose.production.yml logs -f
```

### 5. 初始化数据库

```bash
# 执行数据库迁移
chmod +x deploy/scripts/migrate.sh
./deploy/scripts/migrate.sh

# 可选：初始化测试数据
docker-compose -f docker-compose.production.yml exec web_admin python scripts/seed_public_groups.py --groups 3 --activities 3
```

### 6. 配置 Nginx

```bash
# 复制 Nginx 配置
sudo cp deploy/nginx/nginx.conf /etc/nginx/sites-available/redpacket

# 修改配置中的域名
sudo nano /etc/nginx/sites-available/redpacket
# 将 yourdomain.com 替换为实际域名

# 启用配置
sudo ln -s /etc/nginx/sites-available/redpacket /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载 Nginx
sudo systemctl reload nginx
```

### 7. 申请 SSL 证书

```bash
# 安装 Certbot
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

# 申请证书
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 自动续期（已自动配置）
sudo certbot renew --dry-run
```

### 8. 验证部署

```bash
# 运行健康检查
chmod +x deploy/scripts/healthcheck.sh
./deploy/scripts/healthcheck.sh

# 访问服务
# - 前端控制台: https://yourdomain.com
# - Web Admin: https://yourdomain.com/admin/login
# - Grafana: https://yourdomain.com/grafana
```

---

## 详细部署步骤

### 步骤 1: 服务器准备

```bash
# 更新系统
sudo apt-get update && sudo apt-get upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 安装 Nginx
sudo apt-get install -y nginx

# 安装 Certbot
sudo apt-get install -y certbot python3-certbot-nginx
```

---

### 步骤 2: 配置环境变量

编辑 `.env.production` 文件，确保所有必填项都已配置：

```bash
# 生成强随机字符串（用于 JWT 和 Session 密钥）
openssl rand -hex 32

# 编辑环境变量
nano .env.production
```

**安全建议**:
- 所有密钥使用强随机字符串（至少 32 位）
- 数据库密码使用强密码（至少 16 位，包含大小写字母、数字、特殊字符）
- 不要在生产环境设置 `DEBUG=true`

---

### 步骤 3: 数据库初始化

```bash
# 启动数据库服务
docker-compose -f docker-compose.production.yml up -d db

# 等待数据库就绪
sleep 10

# 执行迁移
./deploy/scripts/migrate.sh
```

**验证数据库**:
```bash
# 连接数据库验证
docker-compose -f docker-compose.production.yml exec db psql -U redpacket -d redpacket -c "\dt"
```

---

### 步骤 4: 启动所有服务

```bash
# 启动所有服务
docker-compose -f docker-compose.production.yml up -d

# 查看服务状态
docker-compose -f docker-compose.production.yml ps

# 查看日志
docker-compose -f docker-compose.production.yml logs -f web_admin
docker-compose -f docker-compose.production.yml logs -f miniapp_api
docker-compose -f docker-compose.production.yml logs -f frontend
```

---

### 步骤 5: 配置 Nginx 和 SSL

1. **修改 Nginx 配置**:
   ```bash
   sudo nano /etc/nginx/sites-available/redpacket
   # 将所有 yourdomain.com 替换为实际域名
   ```

2. **测试配置**:
   ```bash
   sudo nginx -t
   ```

3. **启用配置**:
   ```bash
   sudo ln -s /etc/nginx/sites-available/redpacket /etc/nginx/sites-enabled/
   sudo systemctl reload nginx
   ```

4. **申请 SSL 证书**:
   ```bash
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

5. **验证 SSL**:
   ```bash
   curl -I https://yourdomain.com
   ```

---

### 步骤 6: 配置监控

**Prometheus 和 Grafana 已通过 Docker Compose 自动启动**。

1. **访问 Grafana**:
   - URL: `https://yourdomain.com/grafana`
   - 默认用户名: `admin`
   - 默认密码: 在 `.env.production` 中配置的 `GRAFANA_ADMIN_PASSWORD`

2. **配置数据源**:
   - Prometheus 数据源已自动配置（`http://prometheus:9090`）

3. **导入仪表板**（可选）:
   - 可以在 Grafana 中创建自定义仪表板
   - 或使用 Grafana 社区提供的模板

---

## 监控与日志

### Prometheus 指标

**访问地址**: `http://localhost:9090`（仅本地访问）

**抓取目标**:
- Web Admin: `http://web_admin:8000/metrics`
- MiniApp API: `http://miniapp_api:8080/metrics`（如果有）

**指标类型**:
- `app_uptime_seconds`: 应用运行时间
- `app_info`: 应用信息
- 自定义业务指标（通过 `monitoring/metrics.py` 定义）

---

### Grafana 可视化

**访问地址**: `https://yourdomain.com/grafana`

**默认配置**:
- 数据源: Prometheus（自动配置）
- 仪表板: 需要手动创建或导入

**建议仪表板**:
- 应用运行时间
- 请求速率和错误率
- 响应时间分布
- 数据库连接池使用率

---

### 日志管理

**Docker 日志**:
```bash
# 查看所有服务日志
docker-compose -f docker-compose.production.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.production.yml logs -f web_admin
docker-compose -f docker-compose.production.yml logs -f miniapp_api
docker-compose -f docker-compose.production.yml logs -f bot

# 查看最近 100 行日志
docker-compose -f docker-compose.production.yml logs --tail=100 web_admin
```

**日志轮转**:
- Docker 日志驱动已配置 `max-size: 10m` 和 `max-file: 3`
- 每个容器最多保留 3 个 10MB 的日志文件

**Nginx 日志**:
- 访问日志: `/var/log/nginx/redpacket_access.log`
- 错误日志: `/var/log/nginx/redpacket_error.log`

---

## 维护与更新

### 日常维护

**健康检查**:
```bash
# 运行健康检查脚本
./deploy/scripts/healthcheck.sh

# 手动检查服务
curl http://localhost:8000/healthz
curl http://localhost:8080/healthz
curl http://localhost:3001
```

**数据库备份**:
```bash
# 手动备份
docker-compose -f docker-compose.production.yml exec db pg_dump -U redpacket redpacket > backups/backup-$(date +%Y%m%d-%H%M%S).sql

# 设置定时备份（crontab）
# 0 2 * * * cd /path/to/project && docker-compose -f docker-compose.production.yml exec -T db pg_dump -U redpacket redpacket > backups/backup-$(date +\%Y\%m\%d).sql
```

---

### 更新部署

**1. 备份数据库**:
```bash
./deploy/scripts/backup.sh  # 如果存在
# 或手动备份
docker-compose -f docker-compose.production.yml exec db pg_dump -U redpacket redpacket > backups/backup-$(date +%Y%m%d-%H%M%S).sql
```

**2. 拉取最新代码**:
```bash
git pull origin main
```

**3. 重新构建镜像**:
```bash
# 构建后端
docker build -f Dockerfile.backend -t redpacket/backend:latest .

# 构建前端
docker build -f frontend-next/Dockerfile -t redpacket/frontend:latest ./frontend-next
```

**4. 执行数据库迁移**:
```bash
./deploy/scripts/migrate.sh
```

**5. 重启服务**:
```bash
# 滚动重启（零停机）
docker-compose -f docker-compose.production.yml up -d --no-deps --build web_admin
docker-compose -f docker-compose.production.yml up -d --no-deps --build miniapp_api
docker-compose -f docker-compose.production.yml up -d --no-deps --build frontend

# 或完全重启
docker-compose -f docker-compose.production.yml restart
```

**6. 验证更新**:
```bash
./deploy/scripts/healthcheck.sh
```

---

### 回滚

如果新版本有问题，快速回滚：

**1. 代码回滚**:
```bash
git checkout <previous-commit-hash>
```

**2. 数据库回滚**（如果新版本包含数据库变更）:
```bash
# 恢复数据库备份
docker-compose -f docker-compose.production.yml exec -T db psql -U redpacket redpacket < backups/backup-YYYYMMDD-HHMMSS.sql
```

**3. 重新构建和重启**:
```bash
docker-compose -f docker-compose.production.yml up -d --build
```

---

## 故障排查

### 常见问题

#### 1. 服务无法启动

**检查日志**:
```bash
docker-compose -f docker-compose.production.yml logs web_admin
docker-compose -f docker-compose.production.yml logs miniapp_api
```

**检查环境变量**:
```bash
docker-compose -f docker-compose.production.yml exec web_admin env | grep BOT_TOKEN
```

**检查端口占用**:
```bash
sudo netstat -tlnp | grep -E ':(8000|8080|3001|5432)'
```

---

#### 2. 数据库连接失败

**检查数据库状态**:
```bash
docker-compose -f docker-compose.production.yml ps db
docker-compose -f docker-compose.production.yml logs db
```

**测试连接**:
```bash
docker-compose -f docker-compose.production.yml exec web_admin python -c "from models.db import engine; engine.connect(); print('OK')"
```

**检查 DATABASE_URL**:
```bash
docker-compose -f docker-compose.production.yml exec web_admin env | grep DATABASE_URL
```

---

#### 3. 前端无法访问后端 API

**检查 Nginx 配置**:
```bash
sudo nginx -t
sudo tail -f /var/log/nginx/redpacket_error.log
```

**检查后端服务**:
```bash
curl http://localhost:8000/healthz
curl http://localhost:8080/healthz
```

**检查前端环境变量**:
```bash
docker-compose -f docker-compose.production.yml exec frontend env | grep NEXT_PUBLIC
```

---

#### 4. SSL 证书问题

**检查证书**:
```bash
sudo certbot certificates
```

**续期证书**:
```bash
sudo certbot renew
```

**手动申请**:
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com --force-renewal
```

---

### 性能优化

**1. 数据库连接池**:
- 默认配置已足够，如需调整，修改 `models/db.py` 中的连接池参数

**2. Uvicorn Workers**:
- 当前配置: `--workers 2`
- 可根据 CPU 核心数调整（推荐: CPU 核心数 × 2）

**3. Next.js 缓存**:
- 已启用 standalone 输出，优化 Docker 镜像大小

**4. Nginx 缓存**:
- 静态文件已配置缓存（30 天）
- 可根据需要调整缓存策略

---

## 安全建议

### 1. 密钥管理

- ✅ 所有密钥存储在 `.env.production`（不提交到 Git）
- ✅ 使用强随机字符串生成密钥
- ✅ 定期轮换密钥（JWT Secret、Session Secret）

### 2. 网络安全

- ✅ 所有服务仅监听 127.0.0.1（通过 Nginx 反向代理）
- ✅ 使用 HTTPS（Let's Encrypt SSL 证书）
- ✅ 配置防火墙（仅开放 80、443 端口）

### 3. 数据库安全

- ✅ 使用强密码
- ✅ 仅允许本地连接（127.0.0.1）
- ✅ 定期备份
- ✅ 启用 SSL 连接（生产环境推荐）

### 4. 应用安全

- ✅ 设置 `DEBUG=false`
- ✅ 配置安全响应头（CSP、HSTS 等）
- ✅ 限制管理员访问（`ADMIN_IDS`、`SUPER_ADMINS`）
- ✅ 启用登录限流（防止暴力破解）

---

## 备份与恢复

### 数据库备份

**手动备份**:
```bash
docker-compose -f docker-compose.production.yml exec db pg_dump -U redpacket redpacket > backups/backup-$(date +%Y%m%d-%H%M%S).sql
```

**定时备份**（crontab）:
```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天凌晨 2 点备份）
0 2 * * * cd /path/to/project && docker-compose -f docker-compose.production.yml exec -T db pg_dump -U redpacket redpacket > backups/backup-$(date +\%Y\%m\%d).sql
```

### 恢复数据库

```bash
# 恢复备份
docker-compose -f docker-compose.production.yml exec -T db psql -U redpacket redpacket < backups/backup-YYYYMMDD-HHMMSS.sql
```

---

## 监控告警

### Prometheus 告警规则（可选）

创建 `deploy/prometheus/alerts.yml`:

```yaml
groups:
  - name: redpacket_alerts
    rules:
      - alert: ServiceDown
        expr: up{job="web-admin"} == 0
        for: 1m
        annotations:
          summary: "Web Admin 服务下线"
      
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        annotations:
          summary: "错误率过高"
```

### 告警通知

配置 Alertmanager（可选）:
- 发送到邮件
- 发送到 Slack
- 发送到 Telegram

---

## 使用 PM2（可选）

如果不使用 Docker，可以使用 PM2 管理进程：

```bash
# 安装 PM2
npm install -g pm2

# 启动服务
pm2 start deploy/scripts/pm2.ecosystem.config.js

# 查看状态
pm2 status

# 查看日志
pm2 logs

# 保存配置
pm2 save

# 设置开机自启
pm2 startup
```

---

## 快速命令参考

```bash
# 启动所有服务
docker-compose -f docker-compose.production.yml up -d

# 停止所有服务
docker-compose -f docker-compose.production.yml down

# 查看服务状态
docker-compose -f docker-compose.production.yml ps

# 查看日志
docker-compose -f docker-compose.production.yml logs -f

# 重启服务
docker-compose -f docker-compose.production.yml restart

# 执行数据库迁移
./deploy/scripts/migrate.sh

# 健康检查
./deploy/scripts/healthcheck.sh

# 备份数据库
docker-compose -f docker-compose.production.yml exec db pg_dump -U redpacket redpacket > backups/backup-$(date +%Y%m%d-%H%M%S).sql
```

---

## 支持与文档

- **架构说明**: `037_ARCHITECTURE.md`
- **部署指南**: `037_DEPLOY_GUIDE.md`
- **API 对照表**: `037_API_TABLE.md`
- **环境变量配置**: `docs/CONFIG_ENV_MATRIX.md`
- **健康检查**: `docs/HEALTHCHECK_AND_SELFTEST.md`

---

*最后更新: 2025-01-XX*

