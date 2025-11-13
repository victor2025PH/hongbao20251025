# Docker Compose 部署指南

> 使用 Docker Compose 一键部署整个系统

---

## 📋 前置要求

- Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- Docker 20.10+
- Docker Compose 2.0+
- 至少 2GB 内存
- 至少 10GB 可用磁盘空间

---

## 🚀 快速开始

### 步骤 1: 准备服务器

**连接到您的服务器（Ubuntu 24.04）:**

```bash
# SSH 连接到服务器
ssh user@your-server-ip
```

### 步骤 2: 安装 Docker 和 Docker Compose

```bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 重新登录或执行以下命令使 Docker 组权限生效
newgrp docker

# 验证安装
docker --version
docker-compose --version
```

### 步骤 3: 上传项目代码

**方式一: 从 Git 克隆**

```bash
# 创建项目目录
sudo mkdir -p /opt/redpacket
sudo chown $USER:$USER /opt/redpacket
cd /opt/redpacket

# 克隆代码
git clone <your-repo-url> .
```

**方式二: 从本地上传**

```bash
# 在本地执行
scp -r /本地/项目/路径/* user@服务器IP:/opt/redpacket/

# 或使用 rsync
rsync -avz /本地/项目/路径/ user@服务器IP:/opt/redpacket/
```

### 步骤 4: 配置环境变量

```bash
cd /opt/redpacket

# 复制环境变量示例文件
cp .env.production.example .env.production

# 编辑环境变量（必须填入真实值）
nano .env.production
```

**必填配置项:**

```bash
# Telegram Bot Token
BOT_TOKEN=你的Telegram_Bot_Token

# 数据库配置
POSTGRES_PASSWORD=强密码（至少16位）
DATABASE_URL=postgresql+psycopg2://redpacket:${POSTGRES_PASSWORD}@db:5432/redpacket

# 管理员 ID
ADMIN_IDS=你的Telegram_ID

# JWT 密钥（生成强随机字符串）
MINIAPP_JWT_SECRET=$(openssl rand -hex 32)
ADMIN_SESSION_SECRET=$(openssl rand -hex 32)
```

### 步骤 5: 一键部署

```bash
# 赋予执行权限
chmod +x deploy/scripts/deploy_docker_compose.sh

# 运行部署脚本
./deploy/scripts/deploy_docker_compose.sh
```

**脚本会自动完成:**
1. ✅ 检查 Docker 环境
2. ✅ 创建必要目录
3. ✅ 构建 Docker 镜像（后端 + 前端）
4. ✅ 启动数据库并等待就绪
5. ✅ 初始化数据库
6. ✅ 启动所有服务
7. ✅ 执行健康检查

---

## 📊 服务访问

部署完成后，服务将在以下地址可用：

- **后端服务**: `http://服务器IP:8000`
- **MiniApp API**: `http://服务器IP:8080`
- **前端控制台**: `http://服务器IP:3001`

**健康检查:**
```bash
curl http://localhost:8000/healthz
curl http://localhost:8080/healthz
curl http://localhost:3001
```

---

## 🔧 常用命令

### 查看服务状态

```bash
docker-compose -f docker-compose.production.yml ps
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose -f docker-compose.production.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.production.yml logs -f web_admin
docker-compose -f docker-compose.production.yml logs -f miniapp_api
docker-compose -f docker-compose.production.yml logs -f frontend
```

### 重启服务

```bash
# 重启所有服务
docker-compose -f docker-compose.production.yml restart

# 重启特定服务
docker-compose -f docker-compose.production.yml restart web_admin
```

### 停止服务

```bash
# 停止所有服务
docker-compose -f docker-compose.production.yml down

# 停止并删除数据卷（谨慎使用）
docker-compose -f docker-compose.production.yml down -v
```

### 更新服务

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建镜像
docker build -f Dockerfile.backend -t redpacket/backend:latest .
docker build -f frontend-next/Dockerfile -t redpacket/frontend:latest ./frontend-next

# 3. 重启服务
docker-compose -f docker-compose.production.yml up -d --force-recreate
```

---

## 🌐 配置 Nginx 反向代理（推荐）

### 步骤 1: 安装 Nginx

```bash
sudo apt-get update
sudo apt-get install -y nginx
```

### 步骤 2: 配置 Nginx

```bash
# 复制配置文件
sudo cp deploy/nginx/nginx.conf /etc/nginx/sites-available/redpacket

# 修改域名（如果有）
sudo nano /etc/nginx/sites-available/redpacket
# 将所有 yourdomain.com 替换为实际域名

# 启用配置
sudo ln -s /etc/nginx/sites-available/redpacket /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 步骤 3: 申请 SSL 证书

```bash
# 安装 Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# 申请证书
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## 🔍 故障排查

### 服务无法启动

```bash
# 查看服务日志
docker-compose -f docker-compose.production.yml logs web_admin

# 查看容器状态
docker-compose -f docker-compose.production.yml ps

# 检查端口占用
netstat -tlnp | grep -E ':(8000|8080|3001)'
```

### 数据库连接失败

```bash
# 检查数据库容器
docker-compose -f docker-compose.production.yml ps db

# 查看数据库日志
docker-compose -f docker-compose.production.yml logs db

# 测试数据库连接
docker-compose -f docker-compose.production.yml exec db psql -U redpacket -d redpacket -c "SELECT 1"
```

### 镜像构建失败

```bash
# 查看构建日志
docker build -f Dockerfile.backend -t redpacket/backend:latest . --no-cache

# 检查 Dockerfile
cat Dockerfile.backend
```

### 前端无法访问后端 API

```bash
# 检查环境变量
docker-compose -f docker-compose.production.yml exec frontend env | grep NEXT_PUBLIC

# 检查网络连接
docker-compose -f docker-compose.production.yml exec frontend curl http://web_admin:8000/healthz
```

---

## 💾 数据备份

### 备份数据库

```bash
# 手动备份
docker-compose -f docker-compose.production.yml exec db pg_dump -U redpacket redpacket > backups/backup-$(date +%Y%m%d-%H%M%S).sql

# 使用备份脚本
chmod +x deploy/scripts/backup.sh
./deploy/scripts/backup.sh
```

### 恢复数据库

```bash
docker-compose -f docker-compose.production.yml exec -T db psql -U redpacket redpacket < backups/backup-YYYYMMDD-HHMMSS.sql
```

---

## 🔐 安全建议

1. **修改默认密码**: 确保 `.env.production` 中所有密码都是强密码
2. **限制端口访问**: 使用防火墙只开放必要端口（80, 443）
3. **使用 HTTPS**: 配置 SSL 证书
4. **定期备份**: 设置定时备份任务
5. **更新镜像**: 定期更新 Docker 镜像和依赖

---

## 📝 下一步

部署完成后，建议：

1. ✅ 配置 Nginx 反向代理
2. ✅ 申请 SSL 证书
3. ✅ 设置防火墙规则
4. ✅ 配置定时备份
5. ✅ 设置监控告警

---

*最后更新: 2025-01-XX*

