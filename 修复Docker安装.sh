#!/bin/bash
# 修复 Docker 安装错误
# 解决 "Directory nonexistent" 问题

echo "===================================="
echo "🔧 修复 Docker 安装问题"
echo "===================================="
echo ""

# 创建缺失的目录
echo "📁 步骤 1: 创建缺失的目录..."
sudo mkdir -p /etc/apt/sources.list.d
sudo mkdir -p /etc/apt/keyrings

echo "✅ 目录创建完成"
echo ""

# 重新执行 Docker 安装
echo "🐳 步骤 2: 重新安装 Docker..."
curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
sudo sh /tmp/get-docker.sh

echo ""
echo "✅ Docker 安装完成！"
echo ""

# 将用户添加到 docker 组
echo "👤 步骤 3: 将用户添加到 docker 组..."
sudo usermod -aG docker $USER
echo "✅ 用户已添加到 docker 组"
echo ""

# 验证安装
echo "🧪 步骤 4: 验证 Docker 安装..."
docker --version
docker-compose --version || echo "⚠️  Docker Compose 尚未安装"

echo ""
echo "===================================="
echo "✅ 修复完成！"
echo "===================================="
echo ""
echo "⚠️  重要: 请重新登录 SSH 或执行 'newgrp docker' 以使权限生效"
echo ""
