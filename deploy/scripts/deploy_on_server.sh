#!/bin/bash
# 云服务器部署脚本
# 在服务器上执行: bash deploy/scripts/deploy_on_server.sh

set -e  # 遇到错误立即退出

echo "🚀 开始部署红包系统..."
echo ""

# 步骤 1: 进入项目目录
echo "📂 步骤 1: 进入项目目录..."
cd /opt/redpacket || {
    echo "❌ 错误: /opt/redpacket 目录不存在！"
    exit 1
}

# 步骤 2: 拉取最新代码
echo "📥 步骤 2: 拉取最新代码..."
git pull origin master || {
    echo "❌ 错误: Git 拉取失败！"
    exit 1
}

echo "✅ 代码更新成功！"
git log --oneline -1
echo ""

# 步骤 3: 检查环境变量文件
echo "🔍 步骤 3: 检查环境变量配置..."
if [ ! -f .env.production ]; then
    echo "⚠️  警告: .env.production 文件不存在！"
    echo "请先创建并配置 .env.production 文件"
    echo "参考文档: CONFIGURE_ENV_PRODUCTION.md"
    exit 1
fi

# 检查必需的环境变量
if ! grep -q "POSTGRES_PASSWORD" .env.production || grep -q "POSTGRES_PASSWORD=$" .env.production; then
    echo "⚠️  警告: POSTGRES_PASSWORD 未设置或为空！"
    echo "请编辑 .env.production 文件并设置强密码"
    exit 1
fi

echo "✅ 环境变量配置检查通过"
echo ""

# 步骤 4: 构建并启动服务
echo "🔨 步骤 4: 构建 Docker 镜像..."
docker compose -f docker-compose.production.yml build --no-cache frontend || {
    echo "⚠️  警告: 前端构建失败，尝试使用缓存..."
    docker compose -f docker-compose.production.yml build frontend
}

echo "✅ Docker 镜像构建完成"
echo ""

# 步骤 5: 启动所有服务
echo "🚀 步骤 5: 启动所有服务..."
docker compose -f docker-compose.production.yml up -d || {
    echo "❌ 错误: 服务启动失败！"
    docker compose -f docker-compose.production.yml logs --tail 50
    exit 1
}

echo "✅ 服务启动成功"
echo ""

# 步骤 6: 等待服务启动
echo "⏳ 步骤 6: 等待服务启动（30秒）..."
sleep 30

# 步骤 7: 检查服务状态
echo "📊 步骤 7: 检查服务状态..."
docker compose -f docker-compose.production.yml ps

echo ""
echo "🔍 步骤 8: 验证健康检查..."

# 检查数据库
echo "  检查数据库..."
if docker compose -f docker-compose.production.yml exec -T db pg_isready -U redpacket > /dev/null 2>&1; then
    echo "  ✅ 数据库健康检查通过"
else
    echo "  ⚠️  数据库健康检查失败"
fi

# 检查 Web Admin
echo "  检查 Web Admin..."
if curl -f -s http://127.0.0.1:8000/healthz > /dev/null 2>&1; then
    echo "  ✅ Web Admin 健康检查通过"
else
    echo "  ⚠️  Web Admin 健康检查失败"
fi

# 检查 MiniApp API
echo "  检查 MiniApp API..."
if curl -f -s http://127.0.0.1:8080/healthz > /dev/null 2>&1; then
    echo "  ✅ MiniApp API 健康检查通过"
else
    echo "  ⚠️  MiniApp API 健康检查失败"
fi

# 检查前端
echo "  检查前端..."
if curl -f -s http://127.0.0.1:3001 > /dev/null 2>&1; then
    echo "  ✅ 前端服务正常"
else
    echo "  ⚠️  前端服务异常"
fi

echo ""
echo "✅ 部署完成！"
echo ""
echo "📋 后续操作："
echo "  1. 查看服务日志: docker compose -f docker-compose.production.yml logs -f"
echo "  2. 查看服务状态: docker compose -f docker-compose.production.yml ps"
echo "  3. 测试健康检查: curl http://127.0.0.1:8000/healthz"
echo ""
