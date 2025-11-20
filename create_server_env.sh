#!/bin/bash
# 在服务器上创建 .env.production 文件

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

echo ""
echo "===================================="
echo "🔧 在服务器上创建 .env.production 文件"
echo "===================================="
echo ""

ssh -o StrictHostKeyChecking=no "$server" << 'REMOTE_SCRIPT'
cd /opt/redpacket
echo "=== 创建 .env.production 文件 ==="
echo ""

if [ -f .env.production ]; then
    echo "⚠️  .env.production 文件已存在"
    BACKUP_FILE=".env.production.bak.$(date +%Y%m%d-%H%M%S)"
    cp .env.production "$BACKUP_FILE"
    echo "✅ 已备份现有文件到: $BACKUP_FILE"
fi

if [ -f .env.production.example ]; then
    echo "从 .env.production.example 创建 .env.production..."
    cp .env.production.example .env.production
    chmod 600 .env.production
    echo "✅ 已创建 .env.production 文件"
    echo ""
    echo "文件信息:"
    ls -lh .env.production
    echo ""
    echo "⚠️  重要: 请立即编辑 .env.production 文件并填入真实的配置值"
    echo ""
    echo "可以使用以下命令编辑:"
    echo "  nano .env.production"
    echo "  或"
    echo "  vi .env.production"
    echo ""
elif [ -f .env ]; then
    echo "从 .env 创建 .env.production..."
    cp .env .env.production
    chmod 600 .env.production
    echo "✅ 已从 .env 创建 .env.production 文件"
    echo ""
    echo "⚠️  请确认 .env 中的配置是否适合生产环境"
    echo ""
else
    echo "❌ 错误: 找不到模板文件"
    echo "请手动创建 .env.production 文件"
    exit 1
fi
REMOTE_SCRIPT

