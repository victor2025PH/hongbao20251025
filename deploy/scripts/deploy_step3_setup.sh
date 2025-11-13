#!/bin/bash
# 部署步骤 3: 准备项目代码和配置

set -e

echo "📁 开始准备项目代码和配置..."
echo ""

# 获取项目目录
read -p "请输入项目部署目录 (默认: /opt/redpacket): " PROJECT_DIR
PROJECT_DIR=${PROJECT_DIR:-/opt/redpacket}

echo "📂 项目目录: $PROJECT_DIR"
echo ""

# 创建项目目录
echo "📁 创建项目目录..."
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR
cd $PROJECT_DIR
echo "✅ 项目目录创建完成"
echo ""

# 询问代码来源
echo "请选择代码来源:"
echo "1. 从 Git 仓库克隆"
echo "2. 从本地上传（使用 scp 或 rsync）"
read -p "请选择 (1/2): " code_source

if [ "$code_source" = "1" ]; then
    read -p "请输入 Git 仓库地址: " GIT_REPO
    echo "📥 克隆代码仓库..."
    git clone $GIT_REPO .
    echo "✅ 代码克隆完成"
elif [ "$code_source" = "2" ]; then
    echo "📤 请使用以下命令从本地上传代码:"
    echo "   scp -r /本地/项目/路径/* $USER@服务器IP:$PROJECT_DIR/"
    echo "   或"
    echo "   rsync -avz /本地/项目/路径/ $USER@服务器IP:$PROJECT_DIR/"
    read -p "代码上传完成后按 Enter 继续..."
fi
echo ""

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p logs backups static/uploads exports secrets
echo "✅ 目录创建完成"
echo ""

# 配置环境变量
echo "⚙️  配置环境变量..."
if [ ! -f .env.production ]; then
    if [ -f .env.production.example ]; then
        cp .env.production.example .env.production
        echo "✅ 已从 .env.production.example 创建 .env.production"
        echo "⚠️  请编辑 .env.production 文件，填入真实配置值"
        echo "   使用命令: nano .env.production"
    else
        echo "⚠️  .env.production.example 不存在，请手动创建 .env.production"
    fi
else
    echo "✅ .env.production 已存在"
fi
echo ""

# 设置文件权限
echo "🔐 设置文件权限..."
chmod 600 .env.production 2>/dev/null || true
chmod 600 secrets/*.json 2>/dev/null || true
echo "✅ 权限设置完成"
echo ""

echo "✅ 项目准备完成"
echo ""
echo "下一步: 安装依赖和初始化数据库"

