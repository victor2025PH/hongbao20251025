#!/bin/bash
# 数据库同步问题修复脚本

set -e

echo "=========================================="
echo "数据库同步问题修复脚本"
echo "=========================================="
echo ""

# 1. 创建共享数据目录
echo "[1/5] 创建共享数据目录..."
mkdir -p data
chmod 755 data
echo "✅ 数据目录创建完成: ./data"
echo ""

# 2. 检查现有数据库文件
echo "[2/5] 检查现有数据库文件..."
if [ -f "./data.sqlite" ]; then
    echo "发现根目录的 data.sqlite 文件"
    read -p "是否移动到 ./data/ 目录？(y/n): " move_file
    if [ "$move_file" = "y" ] || [ "$move_file" = "Y" ]; then
        mv ./data.sqlite ./data/data.sqlite
        echo "✅ 文件已移动: ./data.sqlite -> ./data/data.sqlite"
    fi
fi
echo ""

# 3. 检查容器中的数据库文件
echo "[3/5] 检查容器中的数据库文件..."
BOT_DB_EXISTS=$(docker compose exec -T bot ls /app/data.sqlite 2>/dev/null | wc -l || echo "0")
WEB_ADMIN_DB_EXISTS=$(docker compose exec -T web_admin ls /app/data.sqlite 2>/dev/null | wc -l || echo "0")

if [ "$BOT_DB_EXISTS" -gt 0 ] || [ "$WEB_ADMIN_DB_EXISTS" -gt 0 ]; then
    echo "⚠️  发现容器内有数据库文件"
    echo "建议："
    echo "  1. 如果 bot 容器有数据，先备份："
    echo "     docker compose exec bot cp /app/data.sqlite /app/data.sqlite.backup"
    echo "  2. 如果 web_admin 容器有数据，先备份："
    echo "     docker compose exec web_admin cp /app/data.sqlite /app/data.sqlite.backup"
    echo "  3. 选择保留哪个容器的数据（通常保留 bot 的）"
    read -p "是否继续？(y/n): " continue_choice
    if [ "$continue_choice" != "y" ] && [ "$continue_choice" != "Y" ]; then
        echo "❌ 已取消"
        exit 1
    fi
fi
echo ""

# 4. 检查环境变量配置
echo "[4/5] 检查环境变量配置..."
if [ -f ".env" ]; then
    CURRENT_DB_URL=$(grep "^DATABASE_URL=" .env | cut -d'=' -f2- || echo "")
    if [ -z "$CURRENT_DB_URL" ]; then
        echo "⚠️  .env 文件中没有 DATABASE_URL"
        echo "建议添加：DATABASE_URL=sqlite:////app/data/data.sqlite"
    elif [[ "$CURRENT_DB_URL" == *"sqlite"* ]]; then
        if [[ "$CURRENT_DB_URL" == *"/data/data.sqlite"* ]]; then
            echo "✅ DATABASE_URL 已正确配置为共享路径"
        else
            echo "⚠️  DATABASE_URL 需要更新为共享路径"
            echo "当前值: $CURRENT_DB_URL"
            echo "建议值: sqlite:////app/data/data.sqlite"
            read -p "是否自动更新 .env 文件？(y/n): " update_env
            if [ "$update_env" = "y" ] || [ "$update_env" = "Y" ]; then
                sed -i.bak 's|^DATABASE_URL=.*|DATABASE_URL=sqlite:////app/data/data.sqlite|' .env
                echo "✅ .env 文件已更新（备份为 .env.bak）"
            fi
        fi
    else
        echo "ℹ️  当前使用 PostgreSQL: $CURRENT_DB_URL"
        echo "如果使用 PostgreSQL，请确保所有容器都连接到同一个数据库"
    fi
else
    echo "⚠️  未找到 .env 文件，将使用 docker-compose.yml 中的默认值"
    echo "建议创建 .env 文件并设置: DATABASE_URL=sqlite:////app/data/data.sqlite"
fi
echo ""

# 5. 重启服务
echo "[5/5] 重启服务以应用更改..."
read -p "是否立即重启服务？(y/n): " restart_choice
if [ "$restart_choice" = "y" ] || [ "$restart_choice" = "Y" ]; then
    echo "停止现有服务..."
    docker compose down
    
    echo "启动服务..."
    docker compose up -d
    
    echo "等待服务启动..."
    sleep 5
    
    echo "验证数据库同步..."
    echo ""
    echo "检查 bot 容器数据库路径："
    docker compose exec bot python -c "from models.db import DATABASE_URL; print(f'  DATABASE_URL: {DATABASE_URL}')"
    
    echo "检查 web_admin 容器数据库路径："
    docker compose exec web_admin python -c "from models.db import DATABASE_URL; print(f'  DATABASE_URL: {DATABASE_URL}')"
    
    echo ""
    echo "✅ 服务已重启"
    echo ""
    echo "下一步："
    echo "  1. 访问 http://localhost:8000/admin/dashboard 查看数据"
    echo "  2. 访问 http://localhost:3001 查看前端页面"
    echo "  3. 发布一个红包测试数据同步"
else
    echo "ℹ️  请手动重启服务："
    echo "  docker compose down"
    echo "  docker compose up -d"
fi

echo ""
echo "=========================================="
echo "修复脚本执行完成"
echo "=========================================="

