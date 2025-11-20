# 远程服务器部署步骤

> 由于 GitHub 文件路径问题，请使用以下方法在服务器上部署

---

## 🚀 方法 1: 先克隆代码再部署（推荐）

### 步骤 1: 登录服务器

```bash
ssh ubuntu@165.154.254.99
# 输入密码
```

### 步骤 2: 克隆代码

```bash
# 创建项目目录
sudo mkdir -p /opt/redpacket
sudo chown $USER:$USER /opt/redpacket
cd /opt/redpacket

# 克隆代码
git clone https://github.com/victor2025PH/hongbao20251025.git .
```

### 步骤 3: 运行自动部署脚本

```bash
# 赋予执行权限
chmod +x deploy/auto_deploy.sh
chmod +x deploy/remote_deploy.sh

# 运行自动部署（需要 sudo）
sudo bash deploy/auto_deploy.sh
```

---

## 🚀 方法 2: 使用远程部署脚本

如果已经克隆了代码，可以直接运行：

```bash
cd /opt/redpacket
sudo bash deploy/remote_deploy.sh
```

这个脚本会：
1. 自动创建项目目录
2. 克隆或更新代码
3. 运行自动部署脚本

---

## 🚀 方法 3: 手动执行部署步骤

如果自动脚本有问题，可以手动执行：

### 1. 安装 Docker

```bash
# 更新包索引
sudo apt-get update

# 安装依赖
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 添加 Docker 官方 GPG 密钥
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# 设置 Docker 仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户添加到 docker 组（可选，避免每次都用 sudo）
sudo usermod -aG docker $USER
```

**注意**: 如果添加了用户到 docker 组，需要重新登录或执行 `newgrp docker`

### 2. 克隆代码

```bash
sudo mkdir -p /opt/redpacket
sudo chown $USER:$USER /opt/redpacket
cd /opt/redpacket
git clone https://github.com/victor2025PH/hongbao20251025.git .
```

### 3. 配置环境变量

```bash
cd /opt/redpacket

# 从示例文件创建配置
cp .env.production.example .env.production

# 编辑配置
nano .env.production
```

**必需配置项:**
- `POSTGRES_PASSWORD` - 数据库密码（至少16位）
- `BOT_TOKEN` - Telegram Bot Token
- `ADMIN_IDS` - 您的 Telegram ID
- `MINIAPP_JWT_SECRET` - 运行 `openssl rand -hex 32` 生成
- `ADMIN_SESSION_SECRET` - 运行 `openssl rand -hex 32` 生成

### 4. 启动服务

```bash
cd /opt/redpacket

# 构建并启动服务
docker compose -f docker-compose.production.yml build
docker compose -f docker-compose.production.yml up -d
```

### 5. 验证部署

```bash
# 查看服务状态
docker compose -f docker-compose.production.yml ps

# 检查健康状态
curl http://localhost:8000/healthz

# 查看日志
docker compose -f docker-compose.production.yml logs -f
```

---

## 🔍 故障排查

### 问题 1: Git 克隆失败

```bash
# 检查网络连接
ping github.com

# 如果 GitHub 访问受限，可以：
# 1. 使用代理
# 2. 或手动上传代码到服务器
```

### 问题 2: Docker 安装失败

```bash
# 检查系统版本
lsb_release -a

# 检查是否有其他 Docker 版本
sudo apt-get remove docker docker-engine docker.io containerd runc

# 重新安装
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
```

### 问题 3: 端口被占用

```bash
# 查找占用端口的进程
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :3001

# 停止占用端口的进程
sudo kill -9 <进程ID>
```

### 问题 4: 权限问题

```bash
# 确保当前用户在 docker 组中
groups

# 如果不在，添加用户到 docker 组
sudo usermod -aG docker $USER
newgrp docker
```

---

## 📝 常用命令

```bash
# 查看服务状态
docker compose -f docker-compose.production.yml ps

# 查看日志
docker compose -f docker-compose.production.yml logs -f

# 重启服务
docker compose -f docker-compose.production.yml restart

# 停止服务
docker compose -f docker-compose.production.yml down

# 更新代码并重新部署
cd /opt/redpacket
git pull origin master
docker compose -f docker-compose.production.yml down
docker compose -f docker-compose.production.yml build
docker compose -f docker-compose.production.yml up -d
```

---

## 🌐 访问服务

部署成功后，可以通过以下地址访问：

- **后端 API**: `http://165.154.254.99:8000`
- **前端控制台**: `http://165.154.254.99:3001`
- **健康检查**: `http://165.154.254.99:8000/healthz`

### 配置防火墙

```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 8000/tcp
sudo ufw allow 3001/tcp
sudo ufw reload

# 查看防火墙状态
sudo ufw status
```

---

*最后更新: 2025-01-XX*

