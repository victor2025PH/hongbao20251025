#!/bin/bash
# 一键安装 Docker 和 Docker Compose 脚本
# 在服务器上一次性执行所有命令

set -e  # 遇到错误立即退出

echo "===================================="
echo "🚀 开始安装 Docker 和 Docker Compose"
echo "===================================="
echo ""

# 步骤 1: 更新系统包
echo "📦 步骤 1: 更新系统包..."
sudo apt-get update
echo "✅ 系统更新完成"
echo ""

# 步骤 2: 安装必要的工具
echo "📦 步骤 2: 安装必要的工具 (curl, wget, git)..."
sudo apt-get install -y curl wget git
echo "✅ 工具安装完成"
echo ""

# 步骤 3: 安装 Docker
echo "🐳 步骤 3: 安装 Docker..."
if command -v docker &> /dev/null; then
    echo "✅ Docker 已安装: $(docker --version)"
else
    curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
    sudo sh /tmp/get-docker.sh
    rm /tmp/get-docker.sh
    echo "✅ Docker 安装完成"
fi
echo ""

# 步骤 4: 将当前用户添加到 docker 组
echo "👤 步骤 4: 将当前用户添加到 docker 组..."
sudo usermod -aG docker $USER
echo "✅ 用户已添加到 docker 组"
echo ""

# 步骤 5: 使组权限生效（需要新会话，但先尝试）
echo "🔄 步骤 5: 使组权限生效..."
newgrp docker << END
echo "✅ Docker 组权限已生效"
END
echo ""

# 步骤 6: 验证 Docker 安装
echo "🧪 步骤 6: 验证 Docker 安装..."
docker --version
echo ""

# 步骤 7: 安装 Docker Compose
echo "🐙 步骤 7: 安装 Docker Compose..."
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose 已安装: $(docker-compose --version)"
else
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose 安装完成"
fi
echo ""

# 步骤 8: 验证 Docker Compose 安装
echo "🧪 步骤 8: 验证 Docker Compose 安装..."
docker-compose --version
echo ""

# 步骤 9: 启动 Docker 服务并设置开机自启
echo "🔄 步骤 9: 启动 Docker 服务并设置开机自启..."
sudo systemctl start docker
sudo systemctl enable docker
echo "✅ Docker 服务已启动并设置开机自启"
echo ""

# 步骤 10: 测试 Docker
echo "🧪 步骤 10: 测试 Docker..."
docker run hello-world
echo ""

echo "===================================="
echo "✅ Docker 环境已准备就绪！"
echo "===================================="
echo ""
echo "⚠️  注意: 如果这是首次将用户添加到 docker 组，"
echo "   您需要重新登录 SSH 才能使权限生效，"
echo "   或者执行: newgrp docker"
echo ""
