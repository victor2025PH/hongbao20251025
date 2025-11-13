#!/bin/bash
# Docker Compose 部署脚本（完整版）

set -e

echo "🐳 开始 Docker Compose 部署..."
echo ""

# 检查 Docker 和 Docker Compose
echo "🔍 检查 Docker 环境..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，正在安装..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker 安装完成"
    echo "⚠️  请重新登录以使 Docker 组权限生效，或执行: newgrp docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，正在安装..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose 安装完成"
fi

echo "✅ Docker 环境检查通过"
docker --version
docker-compose --version
echo ""

# 检查项目目录
if [ ! -f "docker-compose.production.yml" ]; then
    echo "❌ 错误: 未找到 docker-compose.production.yml"
    echo "   请确保在项目根目录执行此脚本"
    exit 1
fi

# 检查环境变量文件
echo "⚙️  检查环境变量配置..."
if [ ! -f .env.production ]; then
    if [ -f .env.production.example ]; then
        echo "📝 从示例文件创建 .env.production..."
        cp .env.production.example .env.production
        echo "✅ .env.production 已创建"
        echo ""
        echo "⚠️  重要: 请编辑 .env.production 文件，填入真实配置值"
        echo "   使用命令: nano .env.production"
        echo ""
        read -p "编辑完成后按 Enter 继续..."
    else
        echo "❌ 错误: 未找到 .env.production 或 .env.production.example"
        exit 1
    fi
else
    echo "✅ .env.production 已存在"
fi
echo ""

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p logs backups static/uploads exports secrets
echo "✅ 目录创建完成"
echo ""

# 检查密钥文件
echo "🔐 检查密钥文件..."
if [ ! -f secrets/service_account.json ]; then
    echo "⚠️  secrets/service_account.json 不存在"
    echo "   如果使用 Google Sheet 功能，请上传此文件"
    read -p "是否继续? (y/n): " continue_without_secrets
    if [ "$continue_without_secrets" != "y" ]; then
        exit 1
    fi
else
    echo "✅ service_account.json 已存在"
fi
echo ""

# 构建 Docker 镜像
echo "🏗️  构建 Docker 镜像..."
echo "这可能需要几分钟时间，请耐心等待..."
echo ""

# 构建后端镜像
echo "📦 构建后端镜像..."
docker build -f Dockerfile.backend -t redpacket/backend:latest .
if [ $? -eq 0 ]; then
    echo "✅ 后端镜像构建完成"
else
    echo "❌ 后端镜像构建失败"
    exit 1
fi
echo ""

# 构建前端镜像
if [ -d "frontend-next" ]; then
    echo "📦 构建前端镜像..."
    docker build -f frontend-next/Dockerfile -t redpacket/frontend:latest ./frontend-next
    if [ $? -eq 0 ]; then
        echo "✅ 前端镜像构建完成"
    else
        echo "❌ 前端镜像构建失败"
        exit 1
    fi
else
    echo "⚠️  frontend-next 目录不存在，跳过前端镜像构建"
fi
echo ""

# 启动数据库服务（先启动数据库，等待就绪）
echo "🗄️  启动数据库服务..."
docker-compose -f docker-compose.production.yml up -d db
echo "⏳ 等待数据库就绪（30秒）..."
sleep 30

# 检查数据库健康状态
echo "🔍 检查数据库状态..."
for i in {1..10}; do
    if docker-compose -f docker-compose.production.yml exec -T db pg_isready -U ${POSTGRES_USER:-redpacket} > /dev/null 2>&1; then
        echo "✅ 数据库已就绪"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "❌ 数据库启动超时"
        exit 1
    fi
    echo "   等待中... ($i/10)"
    sleep 3
done
echo ""

# 初始化数据库
echo "🗄️  初始化数据库..."
if [ -f "deploy/scripts/migrate.sh" ]; then
    # 在 Docker 容器中执行迁移
    docker-compose -f docker-compose.production.yml run --rm web_admin python -c "
from models.db import init_db
try:
    init_db()
    print('✅ 数据库初始化成功')
except Exception as e:
    print(f'❌ 数据库初始化失败: {e}')
    exit(1)
"
else
    docker-compose -f docker-compose.production.yml run --rm web_admin python -c "
from models.db import init_db
init_db()
print('✅ 数据库初始化完成')
"
fi
echo ""

# 启动所有服务
echo "🚀 启动所有服务..."
docker-compose -f docker-compose.production.yml up -d
echo ""

# 等待服务启动
echo "⏳ 等待服务启动（15秒）..."
sleep 15
echo ""

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose -f docker-compose.production.yml ps
echo ""

# 健康检查
echo "🏥 执行健康检查..."
echo ""

# 检查后端服务
echo "检查后端服务 (端口 8000)..."
for i in {1..10}; do
    if curl -f -s http://localhost:8000/healthz > /dev/null 2>&1; then
        echo "✅ 后端服务健康检查通过"
        curl -s http://localhost:8000/healthz | python3 -m json.tool 2>/dev/null || echo "响应: $(curl -s http://localhost:8000/healthz)"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "⚠️  后端服务健康检查失败，请查看日志: docker-compose logs web_admin"
    else
        sleep 2
    fi
done
echo ""

# 检查 MiniApp API
echo "检查 MiniApp API (端口 8080)..."
for i in {1..10}; do
    if curl -f -s http://localhost:8080/healthz > /dev/null 2>&1; then
        echo "✅ MiniApp API 健康检查通过"
        curl -s http://localhost:8080/healthz | python3 -m json.tool 2>/dev/null || echo "响应: $(curl -s http://localhost:8080/healthz)"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "⚠️  MiniApp API 健康检查失败，请查看日志: docker-compose logs miniapp_api"
    else
        sleep 2
    fi
done
echo ""

# 检查前端服务
echo "检查前端服务 (端口 3001)..."
for i in {1..10}; do
    if curl -f -s http://localhost:3001 > /dev/null 2>&1; then
        echo "✅ 前端服务响应正常"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "⚠️  前端服务响应异常，请查看日志: docker-compose logs frontend"
    else
        sleep 2
    fi
done
echo ""

echo "✅ Docker Compose 部署完成！"
echo ""
echo "📊 服务访问地址:"
echo "=================="
echo "后端服务: http://localhost:8000"
echo "  - 健康检查: http://localhost:8000/healthz"
echo "  - API 文档: http://localhost:8000/docs"
echo ""
echo "MiniApp API: http://localhost:8080"
echo "  - 健康检查: http://localhost:8080/healthz"
echo ""
echo "前端控制台: http://localhost:3001"
echo "  - Dashboard: http://localhost:3001/"
echo ""
echo "📝 常用命令:"
echo "============"
echo "查看服务状态: docker-compose -f docker-compose.production.yml ps"
echo "查看日志: docker-compose -f docker-compose.production.yml logs -f"
echo "停止服务: docker-compose -f docker-compose.production.yml down"
echo "重启服务: docker-compose -f docker-compose.production.yml restart"
echo "查看特定服务日志: docker-compose -f docker-compose.production.yml logs -f web_admin"
echo ""
echo "🔧 下一步: 配置 Nginx 反向代理（可选）"
echo "   运行: ./deploy/scripts/deploy_step6_nginx.sh"

