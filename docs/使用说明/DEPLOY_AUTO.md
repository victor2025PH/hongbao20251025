# 全自动部署指南

> 在远程服务器上一键自动安装和部署红包系统

---

## 🚀 快速开始

### 前提条件

1. **已登录到远程服务器**（Ubuntu 20.04+ 或 Debian 11+）
2. **具有 root 权限**（或可以使用 sudo）
3. **服务器可以访问互联网**（用于下载依赖）

---

## 📋 部署步骤

### 方法 1: 全自动部署（推荐）

**适用于首次部署或全新服务器**

```bash
# 1. 登录到服务器
ssh ubuntu@您的服务器IP
# 或
ssh root@您的服务器IP

# 2. 下载部署脚本
curl -fsSL https://raw.githubusercontent.com/victor2025PH/hongbao20251025/master/deploy/auto_deploy.sh -o /tmp/auto_deploy.sh

# 或者，如果已经克隆了代码：
cd /opt/redpacket
bash deploy/auto_deploy.sh
```

**如果代码还未克隆，使用以下命令：**

```bash
# 创建项目目录
sudo mkdir -p /opt/redpacket
sudo chown $USER:$USER /opt/redpacket
cd /opt/redpacket

# 克隆代码
git clone https://github.com/victor2025PH/hongbao20251025.git .

# 运行自动部署脚本
sudo bash deploy/auto_deploy.sh
```

---

### 方法 2: 分步执行（更灵活）

如果您想逐步执行，可以手动运行脚本中的各个步骤：

```bash
# 1. 检查环境
bash deploy/scripts/deploy_step1_check.sh

# 2. 安装 Docker
bash deploy/scripts/deploy_step2_install.sh

# 3. 设置项目目录
bash deploy/scripts/deploy_step3_setup.sh

# 4. 克隆代码
cd /opt/redpacket
git clone https://github.com/victor2025PH/hongbao20251025.git .

# 5. 配置环境变量
cp .env.production.example .env.production
nano .env.production  # 编辑配置

# 6. 启动服务
docker compose -f docker-compose.production.yml up -d
```

---

## 🔧 自动部署脚本功能

全自动部署脚本 (`deploy/auto_deploy.sh`) 会执行以下操作：

### ✅ 步骤 1: 检查系统环境
- 检查操作系统版本
- 检查内存和磁盘空间
- 检查端口占用情况

### ✅ 步骤 2: 安装 Docker
- 自动安装 Docker Engine
- 配置 Docker 服务自启动

### ✅ 步骤 3: 安装 Docker Compose
- 安装 Docker Compose（通常包含在 Docker 中）

### ✅ 步骤 4: 创建项目目录
- 创建 `/opt/redpacket` 目录
- 创建备份目录

### ✅ 步骤 5: 克隆/更新代码
- 从 GitHub 克隆代码
- 或更新现有代码

### ✅ 步骤 6: 配置环境变量
- 从示例文件创建 `.env.production`
- 提示编辑配置（可选）

### ✅ 步骤 7: 初始化数据库
- 准备数据库初始化（Docker Compose 会自动处理）

### ✅ 步骤 8: 构建和启动服务
- 构建 Docker 镜像
- 启动所有服务

### ✅ 步骤 9: 验证部署
- 检查容器状态
- 检查服务健康状态

### ✅ 步骤 10: 显示部署信息
- 显示访问地址
- 显示常用命令

---

## 📝 配置环境变量

部署过程中，脚本会提示您配置环境变量。必需配置项：

### 必需配置

```bash
# 数据库密码（至少16位，包含大小写字母、数字、特殊字符）
POSTGRES_PASSWORD=YourStrongPassword123!

# Telegram Bot Token
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# 管理员 Telegram ID（您的用户ID）
ADMIN_IDS=123456789

# JWT 密钥（运行以下命令生成）
# openssl rand -hex 32
MINIAPP_JWT_SECRET=生成的64位十六进制字符串

# Session 密钥（运行以下命令生成）
# openssl rand -hex 32
ADMIN_SESSION_SECRET=生成的64位十六进制字符串
```

### 生成随机密钥

```bash
# 生成 JWT 密钥
openssl rand -hex 32

# 生成 Session 密钥
openssl rand -hex 32
```

---

## 🔍 验证部署

部署完成后，验证服务是否正常运行：

```bash
# 1. 检查容器状态
docker compose -f docker-compose.production.yml ps

# 2. 检查后端健康状态
curl http://localhost:8000/healthz

# 3. 检查前端
curl http://localhost:3001

# 4. 查看日志
docker compose -f docker-compose.production.yml logs -f
```

---

## 🌐 访问服务

部署成功后，可以通过以下地址访问：

- **后端 API**: `http://您的服务器IP:8000`
- **前端控制台**: `http://您的服务器IP:3001`
- **健康检查**: `http://您的服务器IP:8000/healthz`

### 配置防火墙

如果无法访问，请确保防火墙已开放端口：

```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 8000/tcp
sudo ufw allow 3001/tcp
sudo ufw reload

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=3001/tcp
sudo firewall-cmd --reload
```

---

## 🔄 更新部署

如果代码有更新，使用快速部署脚本：

```bash
cd /opt/redpacket
bash deploy/quick_deploy.sh
```

或者手动更新：

```bash
cd /opt/redpacket
git pull origin master
docker compose -f docker-compose.production.yml down
docker compose -f docker-compose.production.yml build
docker compose -f docker-compose.production.yml up -d
```

---

## 🛠️ 常用命令

### 查看服务状态

```bash
docker compose -f docker-compose.production.yml ps
```

### 查看日志

```bash
# 查看所有服务日志
docker compose -f docker-compose.production.yml logs -f

# 查看特定服务日志
docker compose -f docker-compose.production.yml logs -f backend
docker compose -f docker-compose.production.yml logs -f frontend
```

### 重启服务

```bash
# 重启所有服务
docker compose -f docker-compose.production.yml restart

# 重启特定服务
docker compose -f docker-compose.production.yml restart backend
```

### 停止服务

```bash
docker compose -f docker-compose.production.yml down
```

### 备份数据库

```bash
bash deploy/scripts/backup.sh
```

---

## ⚠️ 故障排查

### 问题 1: 端口被占用

```bash
# 查找占用端口的进程
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :3001

# 停止占用端口的进程
sudo kill -9 <进程ID>
```

### 问题 2: Docker 服务未启动

```bash
# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker
```

### 问题 3: 容器启动失败

```bash
# 查看详细日志
docker compose -f docker-compose.production.yml logs

# 检查环境变量
cat .env.production

# 重新构建镜像
docker compose -f docker-compose.production.yml build --no-cache
```

### 问题 4: 数据库连接失败

```bash
# 检查数据库容器状态
docker compose -f docker-compose.production.yml ps db

# 查看数据库日志
docker compose -f docker-compose.production.yml logs db

# 检查环境变量中的数据库配置
grep POSTGRES .env.production
```

---

## 📞 获取帮助

如果遇到问题：

1. **查看日志**: `docker compose -f docker-compose.production.yml logs -f`
2. **检查容器状态**: `docker compose -f docker-compose.production.yml ps`
3. **查看部署文档**: `README_DEPLOY.md`
4. **查看详细指南**: `DEPLOY_STEP_BY_STEP.md`

---

*最后更新: 2025-01-XX*

