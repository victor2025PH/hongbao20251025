#!/bin/bash
# 快速部署脚本（假设环境已准备好）
# 使用方法: bash deploy/quick_deploy.sh

set -e

PROJECT_DIR="/opt/redpacket"
GIT_REPO="https://github.com/victor2025PH/hongbao20251025.git"

echo "🚀 快速部署开始..."

# 进入项目目录
cd "$PROJECT_DIR" || mkdir -p "$PROJECT_DIR" && cd "$PROJECT_DIR"

# 更新代码
if [ -d ".git" ]; then
    echo "📥 更新代码..."
    git fetch origin
    git reset --hard origin/master || git reset --hard origin/main
else
    echo "📥 克隆代码..."
    git clone "$GIT_REPO" .
fi

# 检查环境变量
if [ ! -f ".env.production" ]; then
    echo "⚠️  未找到 .env.production，请先运行完整部署脚本或手动创建"
    exit 1
fi

# 启动服务
echo "🐳 启动 Docker 服务..."
docker compose -f docker-compose.production.yml down
docker compose -f docker-compose.production.yml build
docker compose -f docker-compose.production.yml up -d

echo "✅ 部署完成！"
echo ""
echo "查看服务状态: docker compose -f docker-compose.production.yml ps"
echo "查看日志: docker compose -f docker-compose.production.yml logs -f"

