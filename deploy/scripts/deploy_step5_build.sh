#!/bin/bash
# 部署步骤 5: 构建前端

set -e

echo "🏗️  开始构建前端..."
echo ""

# 检查前端目录
if [ ! -d "frontend-next" ]; then
    echo "⚠️  frontend-next 目录不存在，跳过前端构建"
    exit 0
fi

cd frontend-next

# 检查环境变量
if [ -f "../.env.production" ]; then
    echo "📝 加载环境变量..."
    export $(cat ../.env.production | grep -v '^#' | grep NEXT_PUBLIC | xargs)
fi

# 构建前端
echo "🏗️  构建 Next.js 应用..."
npm run build
echo "✅ 前端构建完成"
echo ""

cd ..

echo "✅ 构建步骤完成"
echo ""
echo "下一步: 配置 Nginx 和启动服务"

