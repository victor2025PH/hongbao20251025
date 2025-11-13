#!/bin/bash
# 修复部署问题脚本
# 使用方法: bash deploy/fix_deployment_issues.sh

set -e

echo "🔧 开始修复部署问题..."
echo ""

# 1. 修复 Docker 权限
echo "========== 步骤 1: 修复 Docker 权限 =========="
if groups | grep -q docker; then
    echo "✅ 用户已在 docker 组中"
else
    echo "📝 将用户添加到 docker 组..."
    sudo usermod -aG docker $USER
    echo "✅ 用户已添加到 docker 组"
    echo "⚠️  请重新登录或执行: newgrp docker"
    echo ""
    read -p "是否现在执行 newgrp docker? (y/n): " exec_newgrp
    if [ "$exec_newgrp" = "y" ] || [ "$exec_newgrp" = "Y" ]; then
        newgrp docker
    fi
fi
echo ""

# 2. 检查 .env.production 语法错误
echo "========== 步骤 2: 检查 .env.production 语法 =========="
if [ -f ".env.production" ]; then
    echo "📝 检查 .env.production 文件..."
    
    # 查找包含斜杠的变量名（错误格式）
    ERR_LINES=$(grep -n "^[^#]*[^=]*/.*=" .env.production 2>/dev/null || true)
    
    if [ -n "$ERR_LINES" ]; then
        echo "⚠️  发现可能的问题行:"
        echo "$ERR_LINES"
        echo ""
        read -p "是否自动修复（删除包含斜杠的变量名行）? (y/n): " fix_env
        if [ "$fix_env" = "y" ] || [ "$fix_env" = "Y" ]; then
            # 备份原文件
            cp .env.production .env.production.backup.$(date +%Y%m%d_%H%M%S)
            # 删除包含斜杠的变量名行
            sed -i '/^[^#]*[^=]*\/.*=/d' .env.production
            echo "✅ 已修复 .env.production 文件（原文件已备份）"
        else
            echo "⚠️  请手动编辑 .env.production 文件，修复包含斜杠的变量名"
        fi
    else
        echo "✅ 未发现明显的语法错误"
    fi
else
    echo "⚠️  .env.production 文件不存在"
fi
echo ""

# 3. 检查 POSTGRES_PASSWORD
echo "========== 步骤 3: 检查 POSTGRES_PASSWORD =========="
if [ -f ".env.production" ]; then
    if grep -q "^POSTGRES_PASSWORD=" .env.production; then
        PASSWORD=$(grep "^POSTGRES_PASSWORD=" .env.production | cut -d'=' -f2)
        if [ -z "$PASSWORD" ] || [ "$PASSWORD" = "强密码(至少16位)" ] || [ "$PASSWORD" = "强密码" ]; then
            echo "⚠️  POSTGRES_PASSWORD 未设置或使用默认值"
            echo "   请编辑 .env.production 文件，设置强密码"
        else
            echo "✅ POSTGRES_PASSWORD 已设置"
        fi
    else
        echo "⚠️  POSTGRES_PASSWORD 未找到"
        echo "   请编辑 .env.production 文件，添加: POSTGRES_PASSWORD=您的强密码"
    fi
fi
echo ""

# 4. 验证 Docker Compose 配置
echo "========== 步骤 4: 验证 Docker Compose 配置 =========="
if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
    echo "📝 验证 docker-compose.production.yml 配置..."
    if docker compose -f docker-compose.production.yml config > /dev/null 2>&1; then
        echo "✅ Docker Compose 配置有效"
    else
        echo "❌ Docker Compose 配置有错误"
        echo "   运行以下命令查看详细错误:"
        echo "   docker compose -f docker-compose.production.yml config"
    fi
else
    echo "⚠️  Docker Compose 未安装"
fi
echo ""

echo "✅ 修复检查完成！"
echo ""
echo "📋 下一步操作:"
echo "1. 如果 Docker 权限已修复，重新登录或执行: newgrp docker"
echo "2. 确保 .env.production 文件配置正确"
echo "3. 重新构建和启动服务:"
echo "   sudo docker compose -f docker-compose.production.yml build"
echo "   sudo docker compose -f docker-compose.production.yml up -d"

