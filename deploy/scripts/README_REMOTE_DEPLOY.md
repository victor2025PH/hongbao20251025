# 远程部署脚本使用说明

> 简单快速的远程部署方案

---

## 📋 脚本说明

### `deploy_remote.sh` - 本地触发脚本

在本地执行，连接到远程服务器并触发部署。

### `deploy.sh` - 服务器端部署脚本

在远程服务器上执行，完成实际的部署工作。

---

## 🚀 快速开始

### 方法 1: 使用 Makefile（推荐）

```bash
# 设置环境变量
export DEPLOY_HOST=165.154.233.55
export DEPLOY_USER=ubuntu
export DEPLOY_PATH=/opt/redpacket
export DEPLOY_BRANCH=master

# 执行部署
make deploy-remote
```

### 方法 2: 直接运行脚本

```bash
# 设置环境变量
export DEPLOY_HOST=165.154.233.55
export DEPLOY_USER=ubuntu
export DEPLOY_PATH=/opt/redpacket

# 执行部署（默认 master 分支）
bash deploy/scripts/deploy_remote.sh

# 或指定分支
bash deploy/scripts/deploy_remote.sh master
```

### 方法 3: 编辑脚本直接配置

编辑 `deploy/scripts/deploy_remote.sh`，修改开头的配置变量：

```bash
SERVER_USER="ubuntu"
SERVER_IP="165.154.233.55"
PROJECT_DIR="/opt/redpacket"
BRANCH="master"
```

然后执行：
```bash
bash deploy/scripts/deploy_remote.sh
```

---

## ⚙️ 配置变量

可以通过环境变量或修改脚本开头的变量来配置：

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `SERVER_USER` | `ubuntu` | 远程服务器用户名 |
| `SERVER_IP` | `165.154.233.55` | 远程服务器 IP |
| `PROJECT_DIR` | `/opt/redpacket` | 远程项目目录 |
| `BRANCH` | `master` | 要部署的分支 |
| `SSH_KEY` | `~/.ssh/id_rsa` | SSH 私钥路径 |
| `SSH_PORT` | `22` | SSH 端口 |

---

## 🔧 首次使用设置

### 1. 确保服务器上已有项目

```bash
# SSH 登录服务器
ssh ubuntu@服务器IP

# 检查项目目录
cd /opt/redpacket
git status
```

### 2. 上传部署脚本到服务器

首次使用时，`deploy_remote.sh` 会自动上传 `deploy.sh` 到服务器。

你也可以手动上传：

```bash
scp deploy/scripts/deploy.sh ubuntu@服务器IP:/opt/redpacket/deploy/scripts/
ssh ubuntu@服务器IP "chmod +x /opt/redpacket/deploy/scripts/deploy.sh"
```

### 3. 确保服务器环境准备好

```bash
# 在服务器上检查
docker --version
docker compose version
git --version

# 确保 .env.production 文件存在
ls -la /opt/redpacket/.env.production
```

---

## 📝 部署流程

执行 `deploy_remote.sh` 后，会自动执行以下步骤：

1. ✅ **SSH 连接测试** - 验证可以连接到服务器
2. ✅ **检查远程脚本** - 确保 `deploy.sh` 存在（不存在则自动上传）
3. ✅ **执行远程部署** - 在服务器上运行 `deploy.sh`
4. ✅ **返回结果** - 显示部署成功或失败

服务器端的 `deploy.sh` 会执行：

1. 📦 **备份当前版本** - 创建 Git 标签
2. 📥 **拉取最新代码** - Git pull
3. 🔍 **检查环境变量** - 验证 `.env.production`
4. 🛑 **停止现有服务** - Docker Compose down
5. 🗑️ **清理旧镜像**（可选）
6. 🔨 **构建 Docker 镜像** - Docker Compose build
7. 🚀 **启动所有服务** - Docker Compose up
8. ⏳ **等待服务启动** - 60 秒
9. 🏥 **健康检查** - 验证所有服务正常
10. 📊 **显示服务状态** - Docker Compose ps

---

## 🐛 故障排除

### SSH 连接失败

```bash
# 测试 SSH 连接
ssh -i ~/.ssh/id_rsa ubuntu@服务器IP "echo '连接成功'"

# 检查密钥权限
chmod 600 ~/.ssh/id_rsa
```

### 远程脚本不存在

脚本会自动尝试上传，如果失败，手动上传：

```bash
scp deploy/scripts/deploy.sh ubuntu@服务器IP:/opt/redpacket/deploy/scripts/
ssh ubuntu@服务器IP "chmod +x /opt/redpacket/deploy/scripts/deploy.sh"
```

### 部署失败

查看服务器上的部署日志：

```bash
# SSH 登录服务器
ssh ubuntu@服务器IP

# 查看日志
tail -f /opt/redpacket/logs/deploy.log

# 查看服务状态
cd /opt/redpacket
docker compose -f docker-compose.production.yml ps
docker compose -f docker-compose.production.yml logs --tail 100
```

---

## 📚 相关文档

- [完整部署方案](../docs/AUTO_DEPLOY_COMPLETE_GUIDE.md)
- [快速开始指南](../docs/AUTO_DEPLOY_QUICK_START.md)
- [测试检查指南](../docs/DEPLOYMENT_STATUS_AND_TEST.md)

---

## ✅ 优势

- ✅ **简单直接** - 一个命令完成部署
- ✅ **自动化** - 自动处理备份、拉取、构建、启动
- ✅ **安全** - SSH 密钥认证
- ✅ **可回滚** - 自动创建备份标签
- ✅ **健康检查** - 部署后自动验证服务状态

---

**最后更新**: 2025-01-15

