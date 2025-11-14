# 检查部署文件是否存在

> 如果服务器上找不到 `deploy/auto_deploy.sh`，请按照以下步骤检查

---

## 🔍 在服务器上检查

### 步骤 1: 检查当前目录内容

```bash
cd /opt/redpacket

# 列出所有文件和目录
ls -la

# 检查 deploy 目录是否存在
ls -la deploy/

# 检查 deploy 目录下的所有文件
find deploy/ -type f
```

### 步骤 2: 检查 Git 仓库状态

```bash
cd /opt/redpacket

# 检查是否是 Git 仓库
git status

# 检查所有文件
git ls-files | grep deploy

# 检查远程仓库信息
git remote -v

# 检查当前分支
git branch
```

### 步骤 3: 如果文件不存在，重新拉取

```bash
cd /opt/redpacket

# 拉取最新代码
git fetch origin

# 重置到最新版本
git reset --hard origin/master

# 再次检查文件
ls -la deploy/auto_deploy.sh
```

---

## 🚀 如果文件确实不存在

### 方法 1: 手动创建脚本

如果 `deploy/auto_deploy.sh` 不存在，可以手动创建：

```bash
cd /opt/redpacket
mkdir -p deploy

# 创建自动部署脚本
cat > deploy/auto_deploy.sh << 'SCRIPT_END'
#!/bin/bash
# 自动部署脚本内容
# ... (脚本内容)
SCRIPT_END

chmod +x deploy/auto_deploy.sh
```

### 方法 2: 直接从 GitHub 下载

```bash
cd /opt/redpacket
mkdir -p deploy

# 下载部署脚本
curl -fsSL https://raw.githubusercontent.com/victor2025PH/hongbao20251025/master/deploy/auto_deploy.sh -o deploy/auto_deploy.sh

# 赋予执行权限
chmod +x deploy/auto_deploy.sh
```

### 方法 3: 使用替代部署方法

如果自动部署脚本不可用，可以使用 Docker Compose 直接部署：

```bash
cd /opt/redpacket

# 检查 Docker Compose 文件
ls -la docker-compose.production.yml

# 如果存在，直接使用 Docker Compose
docker compose -f docker-compose.production.yml up -d
```

---

## 📋 快速检查命令

在服务器上执行以下命令，检查所有关键文件：

```bash
cd /opt/redpacket

echo "=== 检查关键文件 ==="
echo "1. deploy/auto_deploy.sh:"
[ -f "deploy/auto_deploy.sh" ] && echo "   ✅ 存在" || echo "   ❌ 不存在"

echo "2. docker-compose.production.yml:"
[ -f "docker-compose.production.yml" ] && echo "   ✅ 存在" || echo "   ❌ 不存在"

echo "3. Dockerfile.backend:"
[ -f "Dockerfile.backend" ] && echo "   ✅ 存在" || echo "   ❌ 不存在"

echo "4. .env.production.example:"
[ -f ".env.production.example" ] && echo "   ✅ 存在" || echo "   ❌ 不存在"

echo ""
echo "=== 检查 deploy 目录 ==="
ls -la deploy/ 2>/dev/null || echo "deploy 目录不存在"
```

---

## 🔄 完整重新克隆（如果问题持续）

如果文件确实缺失，完全重新克隆：

```bash
# 完全删除并重新克隆
sudo rm -rf /opt/redpacket
sudo mkdir -p /opt/redpacket
sudo chown $USER:$USER /opt/redpacket
cd /opt/redpacket
git clone https://github.com/victor2025PH/hongbao20251025.git .

# 验证文件
ls -la deploy/auto_deploy.sh
```

---

*最后更新: 2025-01-XX*

