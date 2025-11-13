#!/bin/bash
# 部署步骤 7: 启动服务

set -e

echo "🚀 开始启动服务..."
echo ""

# 检查项目目录
if [ ! -f "requirements.txt" ]; then
    echo "❌ 错误: 未找到 requirements.txt，请确保在项目根目录执行此脚本"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 加载环境变量
if [ -f .env.production ]; then
    export $(cat .env.production | grep -v '^#' | xargs)
fi

# 选择启动方式
echo "请选择启动方式:"
echo "1. 使用 systemd 服务（推荐生产环境）"
echo "2. 使用 PM2（进程管理）"
echo "3. 使用 Docker Compose"
echo "4. 直接运行（开发/测试）"
read -p "请选择 (1/2/3/4): " start_method

case $start_method in
    1)
        echo "📋 配置 systemd 服务..."
        # 这里可以添加 systemd 服务配置脚本
        echo "⚠️  请手动配置 systemd 服务文件"
        echo "   参考文档: README_DEPLOY.md"
        ;;
    2)
        echo "📋 使用 PM2 启动..."
        if command -v pm2 &> /dev/null; then
            pm2 start deploy/scripts/pm2.ecosystem.config.js
            pm2 save
            pm2 startup
            echo "✅ PM2 服务已启动"
        else
            echo "❌ PM2 未安装，请先安装: npm install -g pm2"
            exit 1
        fi
        ;;
    3)
        echo "🐳 使用 Docker Compose 启动..."
        if command -v docker-compose &> /dev/null; then
            docker-compose -f docker-compose.production.yml up -d
            echo "✅ Docker 服务已启动"
        else
            echo "❌ Docker Compose 未安装"
            exit 1
        fi
        ;;
    4)
        echo "▶️  直接启动服务..."
        echo "⚠️  这种方式适合开发/测试，生产环境请使用 systemd 或 PM2"
        
        # 启动后端服务
        echo "🚀 启动后端服务 (Web Admin, 端口 8000)..."
        nohup uvicorn web_admin.main:app --host 0.0.0.0 --port 8000 --workers 2 > logs/web_admin.log 2>&1 &
        echo $! > logs/web_admin.pid
        echo "✅ 后端服务已启动 (PID: $(cat logs/web_admin.pid))"
        
        # 启动 MiniApp API
        echo "🚀 启动 MiniApp API (端口 8080)..."
        nohup uvicorn miniapp.main:app --host 0.0.0.0 --port 8080 --workers 2 > logs/miniapp_api.log 2>&1 &
        echo $! > logs/miniapp_api.pid
        echo "✅ MiniApp API 已启动 (PID: $(cat logs/miniapp_api.pid))"
        
        # 启动前端服务
        if [ -d "frontend-next" ]; then
            echo "🚀 启动前端服务 (端口 3001)..."
            cd frontend-next
            nohup npm start > ../logs/frontend.log 2>&1 &
            echo $! > ../logs/frontend.pid
            cd ..
            echo "✅ 前端服务已启动 (PID: $(cat logs/frontend.pid))"
        fi
        ;;
    *)
        echo "❌ 无效的选择"
        exit 1
        ;;
esac

echo ""
echo "✅ 服务启动完成"
echo ""
echo "下一步: 验证部署"

