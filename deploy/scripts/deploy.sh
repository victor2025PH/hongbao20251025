#!/usr/bin/env bash
# 服务器端部署脚本
# 此脚本在远程服务器上执行
# 使用方法: bash deploy/scripts/deploy.sh [分支名]

set -euo pipefail

# 配置变量
BRANCH="${1:-master}"                                    # 要部署的分支
PROJECT_DIR="${DEPLOY_PATH:-/opt/redpacket}"            # 项目目录
LOG_FILE="${PROJECT_DIR}/logs/deploy.log"               # 部署日志
BACKUP_DIR="${PROJECT_DIR}/backups"                     # 备份目录

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "[$timestamp] $message" | tee -a "$LOG_FILE"
}

# 确保日志目录存在
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$BACKUP_DIR"

echo -e "${BLUE}====================================${NC}"
echo -e "${BLUE}🚀 开始服务器端部署${NC}"
echo -e "${BLUE}====================================${NC}"
log "开始部署，分支: $BRANCH"
echo ""

# 进入项目目录
cd "$PROJECT_DIR" || {
    log "❌ 错误: 项目目录不存在: $PROJECT_DIR"
    exit 1
}

# 步骤 1: 备份当前版本
echo -e "${YELLOW}📦 步骤 1: 备份当前版本...${NC}"
CURRENT_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
BACKUP_TAG="backup-$(date +%Y%m%d-%H%M%S)"

if [ -d ".git" ]; then
    git tag "$BACKUP_TAG" 2>/dev/null || true
    log "✅ 已创建备份标签: $BACKUP_TAG (当前版本: $CURRENT_COMMIT)"
else
    log "⚠️  不是 Git 仓库，跳过备份"
fi
echo ""

# 步骤 2: 拉取最新代码
echo -e "${YELLOW}📥 步骤 2: 拉取最新代码...${NC}"
if [ ! -d ".git" ]; then
    log "❌ 错误: 不是 Git 仓库，无法拉取代码"
    exit 1
fi

# 保存本地更改（如果有）
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
    log "⚠️  检测到未提交的更改，先 stash..."
    git stash push -m "Auto stash before deploy $(date +%Y%m%d-%H%M%S)" || true
fi

# 拉取最新代码
git fetch origin || {
    log "❌ 错误: Git fetch 失败"
    exit 1
}

# 切换到指定分支
git checkout "$BRANCH" 2>/dev/null || git checkout -b "$BRANCH" origin/"$BRANCH"

# 重置到远程分支
git reset --hard "origin/$BRANCH" || {
    log "❌ 错误: Git reset 失败"
    exit 1
}

# 清理未跟踪的文件（保留 .env.production 等重要文件）
git clean -fd -e '.env.production' -e '.env.*' -e 'backups/' -e 'logs/' || true

NEW_COMMIT=$(git rev-parse HEAD)
log "✅ 代码已更新: $CURRENT_COMMIT -> $NEW_COMMIT"
echo ""

# 步骤 3: 检查环境变量文件
echo -e "${YELLOW}🔍 步骤 3: 检查环境变量配置...${NC}"
if [ ! -f ".env.production" ]; then
    log "❌ 错误: .env.production 文件不存在！"
    log "请先创建并配置 .env.production 文件"
    exit 1
fi

# 检查必需的环境变量
if ! grep -q "POSTGRES_PASSWORD" .env.production || grep -q "^POSTGRES_PASSWORD=$" .env.production; then
    log "⚠️  警告: POSTGRES_PASSWORD 未设置或为空"
    log "建议编辑 .env.production 文件并设置强密码"
fi

log "✅ 环境变量配置检查完成"
echo ""

# 步骤 4: 停止现有服务
echo -e "${YELLOW}🛑 步骤 4: 停止现有服务...${NC}"
if [ -f "docker-compose.production.yml" ]; then
    docker compose -f docker-compose.production.yml down --timeout 30 || {
        log "⚠️  停止服务时出现警告，继续执行..."
    }
    log "✅ 服务已停止"
else
    log "⚠️  docker-compose.production.yml 不存在，跳过停止服务"
fi
echo ""

# 步骤 5: 清理旧镜像（可选）
echo -e "${YELLOW}🗑️  步骤 5: 清理旧镜像...${NC}"
read -t 3 -p "是否清理旧镜像? (y/N, 3秒后自动跳过): " CLEANUP || true
if [[ "$CLEANUP" =~ ^[Yy]$ ]]; then
    docker images | grep "redpacket" | awk '{print $3}' | xargs -r docker rmi -f || true
    docker system prune -f || true
    log "✅ 镜像清理完成"
else
    log "⏭️  跳过镜像清理"
fi
echo ""

# 步骤 6: 构建 Docker 镜像
echo -e "${YELLOW}🔨 步骤 6: 构建 Docker 镜像...${NC}"
log "开始构建镜像（这可能需要 5-10 分钟）..."

if [ -f "docker-compose.production.yml" ]; then
    docker compose --env-file .env.production \
        -f docker-compose.production.yml \
        build --no-cache web_admin frontend || {
        log "⚠️  构建失败，尝试使用缓存..."
        docker compose --env-file .env.production \
            -f docker-compose.production.yml \
            build web_admin frontend || {
            log "❌ 错误: Docker 构建失败"
            exit 1
        }
    }
    log "✅ Docker 镜像构建完成"
else
    log "❌ 错误: docker-compose.production.yml 不存在"
    exit 1
fi
echo ""

# 步骤 7: 启动所有服务
echo -e "${YELLOW}🚀 步骤 7: 启动所有服务...${NC}"
docker compose --env-file .env.production \
    -f docker-compose.production.yml \
    up -d || {
    log "❌ 错误: 服务启动失败"
    docker compose -f docker-compose.production.yml logs --tail 50
    exit 1
}

log "✅ 服务启动命令执行成功"
echo ""

# 步骤 8: 等待服务启动
echo -e "${YELLOW}⏳ 步骤 8: 等待服务启动（60秒）...${NC}"
sleep 60
log "等待完成"
echo ""

# 步骤 9: 健康检查
echo -e "${YELLOW}🏥 步骤 9: 执行健康检查...${NC}"
FAILED=0

# 检查 Web Admin
for i in {1..10}; do
    if curl -f -s http://127.0.0.1:8000/healthz > /dev/null 2>&1; then
        log "✅ Web Admin (8000) 健康检查通过"
        break
    fi
    if [ $i -eq 10 ]; then
        log "❌ Web Admin (8000) 健康检查失败"
        FAILED=1
    else
        sleep 5
    fi
done

# 检查 MiniApp API
for i in {1..10}; do
    if curl -f -s http://127.0.0.1:8080/healthz > /dev/null 2>&1; then
        log "✅ MiniApp API (8080) 健康检查通过"
        break
    fi
    if [ $i -eq 10 ]; then
        log "❌ MiniApp API (8080) 健康检查失败"
        FAILED=1
    else
        sleep 5
    fi
done

# 检查 Frontend
for i in {1..10}; do
    if curl -f -s http://127.0.0.1:3001 > /dev/null 2>&1; then
        log "✅ Frontend (3001) 健康检查通过"
        break
    fi
    if [ $i -eq 10 ]; then
        log "❌ Frontend (3001) 健康检查失败"
        FAILED=1
    else
        sleep 5
    fi
done

# 步骤 10: 显示服务状态
echo ""
echo -e "${YELLOW}📊 步骤 10: 服务状态...${NC}"
docker compose -f docker-compose.production.yml ps
echo ""

# 步骤 11: 检查部署结果
if [ $FAILED -eq 1 ]; then
    echo -e "${RED}====================================${NC}"
    echo -e "${RED}⚠️  部分服务健康检查失败${NC}"
    echo -e "${RED}====================================${NC}"
    log "⚠️  部分服务健康检查失败，请检查日志"
    echo ""
    echo "查看日志:"
    echo "  docker compose -f docker-compose.production.yml logs --tail 100"
    echo ""
    echo "如需回滚，运行:"
    echo "  git checkout $BACKUP_TAG"
    echo "  bash deploy/scripts/deploy.sh $BRANCH"
    echo ""
    exit 1
else
    echo -e "${GREEN}====================================${NC}"
    echo -e "${GREEN}✅ 部署成功！${NC}"
    echo -e "${GREEN}====================================${NC}"
    log "✅ 部署成功完成"
    echo ""
    echo "部署信息:"
    echo "  版本: $NEW_COMMIT"
    echo "  备份: $BACKUP_TAG"
    echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "  服务:"
    echo "    - Web Admin: http://127.0.0.1:8000"
    echo "    - MiniApp API: http://127.0.0.1:8080"
    echo "    - Frontend: http://127.0.0.1:3001"
    echo ""
    log "部署完成"
fi

