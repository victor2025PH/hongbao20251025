#!/bin/bash
# 部署步骤 4: 安装依赖和初始化数据库

set -e

echo "📦 开始安装依赖..."
echo ""

# 检查项目目录
if [ ! -f "requirements.txt" ]; then
    echo "❌ 错误: 未找到 requirements.txt，请确保在项目根目录执行此脚本"
    exit 1
fi

# 创建 Python 虚拟环境
echo "🐍 创建 Python 虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 虚拟环境创建完成"
else
    echo "✅ 虚拟环境已存在"
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate
echo "✅ 虚拟环境已激活"
echo ""

# 升级 pip
echo "⬆️  升级 pip..."
pip install --upgrade pip
echo ""

# 安装 Python 依赖
echo "📦 安装 Python 依赖..."
pip install -r requirements.txt
echo "✅ Python 依赖安装完成"
echo ""

# 安装前端依赖
if [ -d "frontend-next" ]; then
    echo "📦 安装前端依赖..."
    cd frontend-next
    if [ ! -d "node_modules" ]; then
        npm install
        echo "✅ 前端依赖安装完成"
    else
        echo "✅ 前端依赖已存在"
    fi
    cd ..
else
    echo "⚠️  frontend-next 目录不存在，跳过前端依赖安装"
fi
echo ""

# 初始化数据库
echo "🗄️  初始化数据库..."
read -p "是否初始化数据库? (y/n): " init_db
if [ "$init_db" = "y" ]; then
    # 检查环境变量
    if [ -f .env.production ]; then
        export $(cat .env.production | grep -v '^#' | xargs)
    fi
    
    # 执行数据库迁移
    if [ -f "deploy/scripts/migrate.sh" ]; then
        chmod +x deploy/scripts/migrate.sh
        ./deploy/scripts/migrate.sh
    else
        python3 -c "from models.db import init_db; init_db(); print('✅ 数据库初始化完成')"
    fi
    echo "✅ 数据库初始化完成"
else
    echo "⏭️  跳过数据库初始化"
fi
echo ""

echo "✅ 依赖安装完成"
echo ""
echo "下一步: 构建前端和启动服务"

