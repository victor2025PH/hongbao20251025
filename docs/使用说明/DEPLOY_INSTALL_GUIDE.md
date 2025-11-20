# Docker 和 Docker Compose 安装指南

> 详细说明在哪里执行命令以及如何安装

---

## 📍 重要说明：在哪里执行命令

**所有命令都在您的云服务器上执行！**

1. **先连接到服务器**（在您的本地电脑上执行）:
   ```bash
   ssh root@您的服务器IP
   # 或
   ssh ubuntu@您的服务器IP
   ```

2. **连接成功后，所有后续命令都在服务器上执行**

---

## 🐳 步骤 1: 安装 Docker

### 在服务器上执行以下命令：

```bash
# 1. 更新系统包（Ubuntu/Debian）
sudo apt-get update

# 2. 安装必要的工具
sudo apt-get install -y curl wget

# 3. 下载并安装 Docker（官方一键安装脚本）
curl -fsSL https://get.docker.com -o get-docker.sh

# 4. 执行安装脚本
sudo sh get-docker.sh

# 5. 将当前用户添加到 docker 组（这样就不需要每次都用 sudo）
sudo usermod -aG docker $USER

# 6. 使组权限生效（二选一）:
#    方式 A: 重新登录 SSH
#    方式 B: 执行以下命令（推荐）
newgrp docker

# 7. 验证 Docker 安装
docker --version
# 应该显示类似: Docker version 24.0.0, build xxxxxx

# 8. 测试 Docker（可选）
docker run hello-world
```

**如果遇到问题：**

```bash
# 检查 Docker 服务状态
sudo systemctl status docker

# 启动 Docker 服务（如果未启动）
sudo systemctl start docker

# 设置 Docker 开机自启
sudo systemctl enable docker
```

---

## 🐙 步骤 2: 安装 Docker Compose

### 在服务器上执行以下命令：

```bash
# 1. 下载 Docker Compose（最新版本）
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 2. 赋予执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 3. 验证安装
docker-compose --version
# 应该显示类似: Docker Compose version v2.24.0
```

**如果下载失败，可以手动指定版本：**

```bash
# 查看最新版本号（在浏览器访问）
# https://github.com/docker/compose/releases

# 然后使用具体版本号下载（例如 v2.24.0）
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

---

## 📦 步骤 3: 使用 Git 上传代码

### 3.1 在服务器上准备项目目录

```bash
# 1. 创建项目目录
sudo mkdir -p /opt/redpacket

# 2. 设置目录所有者（将 $USER 替换为您的用户名，通常是 root 或 ubuntu）
sudo chown $USER:$USER /opt/redpacket

# 3. 进入项目目录
cd /opt/redpacket
```

### 3.2 克隆代码仓库

**方式 A: 如果您的代码在 Git 仓库（GitHub/GitLab/Gitee 等）**

```bash
# 1. 克隆代码（请将 <your-repo-url> 替换为实际仓库地址）
git clone <your-repo-url> .

# 示例：
# git clone https://github.com/username/redpacket.git .
# git clone https://gitee.com/username/redpacket.git .
# git clone git@github.com:username/redpacket.git .

# 2. 如果仓库是私有的，可能需要配置 SSH 密钥或输入用户名密码
```

**方式 B: 如果代码在本地，先推送到 Git 仓库**

在您的本地电脑上（Windows PowerShell）:

```bash
# 1. 进入项目目录
cd E:\002-工作文件\重要程序\红包系统机器人\037重新开发新功能

# 2. 初始化 Git 仓库（如果还没有）
git init

# 3. 添加远程仓库（请替换为您的仓库地址）
git remote add origin <your-repo-url>

# 4. 添加所有文件
git add .

# 5. 提交
git commit -m "Initial commit for deployment"

# 6. 推送到远程仓库
git push -u origin main
# 或
git push -u origin master
```

然后在服务器上克隆：

```bash
cd /opt/redpacket
git clone <your-repo-url> .
```

### 3.3 验证代码已上传

```bash
# 检查文件是否存在
ls -la

# 应该看到以下文件/目录：
# - app.py
# - requirements.txt
# - docker-compose.production.yml
# - Dockerfile.backend
# - frontend-next/
# - web_admin/
# - models/
# - services/
# 等等
```

---

## ✅ 验证安装完成

执行以下命令验证所有工具已正确安装：

```bash
# 检查 Docker
docker --version

# 检查 Docker Compose
docker-compose --version

# 检查 Git
git --version

# 检查项目文件
cd /opt/redpacket
ls -la
```

**如果所有命令都成功，您应该看到：**
- ✅ Docker version x.x.x
- ✅ Docker Compose version vx.x.x
- ✅ git version x.x.x
- ✅ 项目文件列表

---

## 🚀 下一步：开始部署

安装完成后，继续执行部署：

```bash
cd /opt/redpacket

# 1. 配置环境变量
cp .env.production.example .env.production
nano .env.production  # 编辑并填入真实配置

# 2. 运行一键部署脚本
chmod +x deploy/scripts/deploy_docker_compose.sh
./deploy/scripts/deploy_docker_compose.sh
```

---

## ❓ 常见问题

### Q1: 执行 `docker` 命令提示 "permission denied"

**解决方案：**
```bash
# 确保用户已添加到 docker 组
sudo usermod -aG docker $USER

# 重新登录 SSH 或执行
newgrp docker

# 如果还是不行，临时使用 sudo
sudo docker --version
```

### Q2: Docker Compose 下载很慢

**解决方案：**
```bash
# 使用国内镜像（如果在中国）
sudo curl -L "https://get.daocloud.io/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Q3: Git 克隆需要认证

**解决方案：**
```bash
# 方式 1: 使用 SSH 密钥（推荐）
# 在本地生成 SSH 密钥，然后添加到 Git 平台

# 方式 2: 使用 HTTPS + 个人访问令牌
git clone https://username:token@github.com/username/repo.git .

# 方式 3: 使用用户名密码（不推荐，可能被禁用）
git clone https://username@github.com/username/repo.git .
# 然后输入密码
```

### Q4: 如何查看服务器 IP 地址

```bash
# 查看公网 IP
curl ifconfig.me

# 或
curl ip.sb

# 查看内网 IP
ip addr show
# 或
ifconfig
```

---

## 📝 完整命令清单（复制粘贴版）

**在服务器上依次执行：**

```bash
# ===== 安装 Docker =====
sudo apt-get update
sudo apt-get install -y curl wget
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
docker --version

# ===== 安装 Docker Compose =====
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version

# ===== 准备项目目录 =====
sudo mkdir -p /opt/redpacket
sudo chown $USER:$USER /opt/redpacket
cd /opt/redpacket

# ===== 克隆代码（请替换为实际仓库地址）=====
git clone <your-repo-url> .

# ===== 验证 =====
ls -la
```

---

*最后更新: 2025-01-XX*

