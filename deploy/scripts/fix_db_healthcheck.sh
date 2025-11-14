#!/bin/bash
# 修复 redpacket_db 健康检查问题
# 使用方法: bash deploy/scripts/fix_db_healthcheck.sh

set -e

echo "🔧 开始修复 redpacket_db 健康检查问题..."

# 检查是否在项目根目录
if [ ! -f "docker-compose.production.yml" ]; then
    echo "❌ 错误: 请在项目根目录执行此脚本"
    exit 1
fi

# 1. 检查 .env.production 文件
if [ ! -f ".env.production" ]; then
    echo "⚠️  警告: .env.production 文件不存在，正在创建..."
    cat > .env.production << 'EOF'
# PostgreSQL 数据库配置（必需）
POSTGRES_USER=redpacket
POSTGRES_PASSWORD=redpacket123
POSTGRES_DB=redpacket

# 数据库连接 URL（可选，会自动生成）
# DATABASE_URL=postgresql+psycopg2://redpacket:redpacket123@db:5432/redpacket

# 其他配置
FLAG_ENABLE_PUBLIC_GROUPS=1
DEBUG=false
TZ=Asia/Manila
EOF
    echo "✅ 已创建 .env.production 文件（使用默认密码）"
    echo "⚠️  请修改 POSTGRES_PASSWORD 为强密码！"
else
    echo "✅ .env.production 文件存在"
    
    # 检查 POSTGRES_PASSWORD 是否设置
    if ! grep -q "^POSTGRES_PASSWORD=" .env.production; then
        echo "⚠️  警告: POSTGRES_PASSWORD 未设置，正在添加..."
        echo "" >> .env.production
        echo "# PostgreSQL 密码（请修改为强密码）" >> .env.production
        echo "POSTGRES_PASSWORD=redpacket123" >> .env.production
        echo "✅ 已添加 POSTGRES_PASSWORD（使用默认密码）"
        echo "⚠️  请修改 POSTGRES_PASSWORD 为强密码！"
    else
        PASSWORD_VALUE=$(grep "^POSTGRES_PASSWORD=" .env.production | cut -d'=' -f2 | tr -d ' ' | tr -d '"' | tr -d "'")
        if [ -z "$PASSWORD_VALUE" ]; then
            echo "❌ 错误: POSTGRES_PASSWORD 已设置但值为空"
            echo "   请编辑 .env.production 文件，设置 POSTGRES_PASSWORD=你的密码"
            exit 1
        else
            echo "✅ POSTGRES_PASSWORD 已设置（值: ${PASSWORD_VALUE:0:3}***）"
        fi
    fi
fi

# 2. 停止并删除现有容器（如果存在）
echo ""
echo "🛑 停止现有容器..."
docker compose -f docker-compose.production.yml stop db 2>/dev/null || true
docker compose -f docker-compose.production.yml rm -f db 2>/dev/null || true

# 3. 检查 volume 是否需要清理
echo ""
read -p "是否删除现有的数据库 volume？这将删除所有数据！(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  删除数据库 volume..."
    docker volume rm redpacket_db_data 2>/dev/null || true
    echo "✅ 数据库 volume 已删除"
else
    echo "ℹ️  保留现有数据库 volume"
fi

# 4. 启动数据库服务
echo ""
echo "🚀 启动数据库服务..."
docker compose -f docker-compose.production.yml up -d db

# 5. 等待健康检查
echo ""
echo "⏳ 等待数据库健康检查（最多 60 秒）..."
MAX_WAIT=60
ELAPSED=0
while [ $ELAPSED -lt $MAX_WAIT ]; do
    HEALTH=$(docker inspect --format='{{.State.Health.Status}}' redpacket_db 2>/dev/null || echo "none")
    if [ "$HEALTH" = "healthy" ]; then
        echo "✅ 数据库健康检查通过！"
        break
    elif [ "$HEALTH" = "unhealthy" ]; then
        echo "❌ 数据库健康检查失败"
        echo "   查看日志: docker compose -f docker-compose.production.yml logs db"
        exit 1
    fi
    echo "   等待中... ($ELAPSED/$MAX_WAIT 秒) [状态: $HEALTH]"
    sleep 2
    ELAPSED=$((ELAPSED + 2))
done

if [ "$HEALTH" != "healthy" ]; then
    echo "❌ 超时：数据库在 $MAX_WAIT 秒内未通过健康检查"
    echo "   查看日志: docker compose -f docker-compose.production.yml logs db"
    exit 1
fi

# 6. 验证数据库连接
echo ""
echo "🔍 验证数据库连接..."
docker compose -f docker-compose.production.yml exec -T db psql -U redpacket -d redpacket -c "SELECT version();" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 数据库连接成功！"
else
    echo "⚠️  警告: 无法连接到数据库，但健康检查已通过"
fi

# 7. 显示状态
echo ""
echo "📊 服务状态:"
docker compose -f docker-compose.production.yml ps db

echo ""
echo "✅ 修复完成！"
echo ""
echo "下一步:"
echo "  1. 如果使用了默认密码，请修改 .env.production 中的 POSTGRES_PASSWORD"
echo "  2. 启动所有服务: docker compose -f docker-compose.production.yml up -d"
echo "  3. 查看日志: docker compose -f docker-compose.production.yml logs -f"

