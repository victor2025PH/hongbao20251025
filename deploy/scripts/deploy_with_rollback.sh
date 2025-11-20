#!/bin/bash
# 带自动回滚功能的部署脚本
# 使用方法: bash deploy/scripts/deploy_with_rollback.sh

set -e

# 配置
DEPLOY_PATH="${DEPLOY_PATH:-/opt/redpacket}"
MAX_RETRIES=3
HEALTH_CHECK_TIMEOUT=120  # 健康检查超时时间（秒）

echo "===================================="
echo "🚀 自动部署（带回滚功能）"
echo "===================================="
echo ""

cd "$DEPLOY_PATH" || {
    echo "❌ 错误: 项目目录不存在！"
    exit 1
}

# 备份当前版本
echo "📦 备份当前版本..."
CURRENT_COMMIT=$(git rev-parse HEAD)
BACKUP_TAG="backup-$(date +%Y%m%d-%H%M%S)"
git tag "$BACKUP_TAG"
echo "✅ 已创建备份标签: $BACKUP_TAG"
echo ""

# 拉取最新代码
echo "📥 拉取最新代码..."
git fetch origin
git reset --hard origin/master
git clean -fd

NEW_COMMIT=$(git rev-parse HEAD)
echo "✅ 代码已更新: $CURRENT_COMMIT -> $NEW_COMMIT"
echo ""

# 部署函数
deploy() {
    echo "🔨 构建 Docker 镜像..."
    docker compose --env-file .env.production \
        -f docker-compose.production.yml \
        build --no-cache web_admin frontend || {
        echo "⚠️  构建失败，尝试使用缓存..."
        docker compose --env-file .env.production \
            -f docker-compose.production.yml \
            build web_admin frontend
    }
    
    echo ""
    echo "🛑 停止现有服务..."
    docker compose -f docker-compose.production.yml down --timeout 30 || true
    
    echo ""
    echo "🚀 启动所有服务..."
    docker compose --env-file .env.production \
        -f docker-compose.production.yml \
        up -d
    
    echo ""
    echo "⏳ 等待服务启动..."
    sleep 60
}

# 健康检查函数
health_check() {
    local failed=0
    
    echo "🏥 执行健康检查..."
    
    # 检查 Web Admin
    for i in {1..10}; do
        if curl -f -s http://127.0.0.1:8000/healthz > /dev/null 2>&1; then
            echo "✅ Web Admin (8000) 健康检查通过"
            break
        fi
        if [ $i -eq 10 ]; then
            echo "❌ Web Admin (8000) 健康检查失败"
            failed=1
        else
            sleep 5
        fi
    done
    
    # 检查 MiniApp API
    for i in {1..10}; do
        if curl -f -s http://127.0.0.1:8080/healthz > /dev/null 2>&1; then
            echo "✅ MiniApp API (8080) 健康检查通过"
            break
        fi
        if [ $i -eq 10 ]; then
            echo "❌ MiniApp API (8080) 健康检查失败"
            failed=1
        else
            sleep 5
        fi
    done
    
    # 检查 Frontend
    for i in {1..10}; do
        if curl -f -s http://127.0.0.1:3001 > /dev/null 2>&1; then
            echo "✅ Frontend (3001) 健康检查通过"
            break
        fi
        if [ $i -eq 10 ]; then
            echo "❌ Frontend (3001) 健康检查失败"
            failed=1
        else
            sleep 5
        fi
    done
    
    return $failed
}

# 回滚函数
rollback() {
    echo ""
    echo "⚠️  部署失败，开始回滚..."
    echo "回滚到版本: $CURRENT_COMMIT"
    
    # 恢复到上一个版本
    git checkout "$CURRENT_COMMIT"
    
    # 重新部署
    echo ""
    echo "🔨 重新构建（回滚版本）..."
    docker compose --env-file .env.production \
        -f docker-compose.production.yml \
        build --no-cache web_admin frontend || {
        docker compose --env-file .env.production \
            -f docker-compose.production.yml \
            build web_admin frontend
    }
    
    echo ""
    echo "🛑 停止服务..."
    docker compose -f docker-compose.production.yml down --timeout 30 || true
    
    echo ""
    echo "🚀 启动服务（回滚版本）..."
    docker compose --env-file .env.production \
        -f docker-compose.production.yml \
        up -d
    
    echo ""
    echo "⏳ 等待服务启动..."
    sleep 60
    
    # 检查回滚后服务状态
    if health_check; then
        echo ""
        echo "✅ 回滚成功！"
        return 0
    else
        echo ""
        echo "❌ 回滚后服务仍然异常"
        return 1
    fi
}

# 执行部署
retry_count=0
while [ $retry_count -lt $MAX_RETRIES ]; do
    if deploy; then
        if health_check; then
            echo ""
            echo "===================================="
            echo "✅ 部署成功！"
            echo "===================================="
            echo ""
            echo "部署信息:"
            echo "  版本: $NEW_COMMIT"
            echo "  备份: $BACKUP_TAG"
            echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
            echo ""
            
            # 显示服务状态
            echo "📊 服务状态:"
            docker compose -f docker-compose.production.yml ps
            exit 0
        else
            echo ""
            echo "⚠️  健康检查失败（尝试 $((retry_count + 1))/$MAX_RETRIES）"
            retry_count=$((retry_count + 1))
            
            if [ $retry_count -lt $MAX_RETRIES ]; then
                echo "等待 10 秒后重试..."
                sleep 10
            fi
        fi
    else
        echo ""
        echo "❌ 部署失败"
        break
    fi
done

# 如果所有重试都失败，执行回滚
if [ $retry_count -ge $MAX_RETRIES ]; then
    echo ""
    echo "❌ 达到最大重试次数，执行回滚..."
    if rollback; then
        exit 0
    else
        exit 1
    fi
fi

