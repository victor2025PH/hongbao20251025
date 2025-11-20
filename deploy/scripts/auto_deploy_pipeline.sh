#!/bin/bash
# 完全自动化部署 Pipeline
# 使用方法: bash deploy/scripts/auto_deploy_pipeline.sh [服务器IP] [用户名]

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
DEPLOY_HOST="${1:-${DEPLOY_HOST}}"
DEPLOY_USER="${2:-${DEPLOY_USER:-ubuntu}}"
DEPLOY_PORT="${DEPLOY_PORT:-22}"
DEPLOY_PATH="${DEPLOY_PATH:-/opt/redpacket}"
SSH_KEY="${SSH_KEY:-~/.ssh/id_rsa}"

# 检查参数
if [ -z "$DEPLOY_HOST" ]; then
    echo -e "${RED}错误: 请提供服务器 IP 地址${NC}"
    echo "使用方法: $0 <服务器IP> [用户名]"
    echo "或设置环境变量: DEPLOY_HOST=xxx.xxx.xxx.xxx $0"
    exit 1
fi

echo -e "${BLUE}====================================${NC}"
echo -e "${BLUE}🚀 自动化部署 Pipeline${NC}"
echo -e "${BLUE}====================================${NC}"
echo ""
echo "部署配置:"
echo "  服务器: $DEPLOY_USER@$DEPLOY_HOST:$DEPLOY_PORT"
echo "  路径: $DEPLOY_PATH"
echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 步骤 1: 检查本地环境
echo -e "${YELLOW}步骤 1: 检查本地环境...${NC}"
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git 未安装${NC}"
    exit 1
fi
if ! command -v ssh &> /dev/null; then
    echo -e "${RED}❌ SSH 未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 本地环境检查通过${NC}"
echo ""

# 步骤 2: 检查 SSH 连接
echo -e "${YELLOW}步骤 2: 检查 SSH 连接...${NC}"
if ! ssh -i "$SSH_KEY" -p "$DEPLOY_PORT" -o ConnectTimeout=5 \
    -o StrictHostKeyChecking=no \
    "$DEPLOY_USER@$DEPLOY_HOST" "echo 'SSH 连接成功'" &> /dev/null; then
    echo -e "${RED}❌ SSH 连接失败${NC}"
    echo "请检查:"
    echo "  1. 服务器 IP 是否正确"
    echo "  2. SSH 密钥是否正确配置"
    echo "  3. 服务器是否允许 SSH 连接"
    exit 1
fi
echo -e "${GREEN}✅ SSH 连接成功${NC}"
echo ""

# 步骤 3: 提交并推送代码（如果需要）
echo -e "${YELLOW}步骤 3: 检查本地代码状态...${NC}"
if [ -n "$(git status --porcelain)" ]; then
    echo "检测到未提交的更改:"
    git status --short
    read -p "是否提交并推送? (y/N): " confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        git add .
        read -p "请输入提交信息: " commit_msg
        commit_msg="${commit_msg:-Auto deploy $(date +%Y%m%d-%H%M%S)}"
        git commit -m "$commit_msg"
        git push origin master
        echo -e "${GREEN}✅ 代码已提交并推送${NC}"
    else
        echo -e "${YELLOW}⚠️  跳过提交${NC}"
    fi
else
    echo -e "${GREEN}✅ 工作区干净${NC}"
fi
echo ""

# 步骤 4: 获取当前版本信息
COMMIT_SHA=$(git rev-parse --short HEAD)
COMMIT_MSG=$(git log -1 --pretty=%B)
BRANCH=$(git branch --show-current)

echo "部署信息:"
echo "  分支: $BRANCH"
echo "  提交: $COMMIT_SHA"
echo "  消息: $COMMIT_MSG"
echo ""

# 步骤 5: 在服务器上执行部署
echo -e "${YELLOW}步骤 5: 在服务器上执行部署...${NC}"
ssh -i "$SSH_KEY" \
    -p "$DEPLOY_PORT" \
    -o StrictHostKeyChecking=no \
    "$DEPLOY_USER@$DEPLOY_HOST" \
    "bash -s" << DEPLOY_SCRIPT
set -e

cd "$DEPLOY_PATH" || {
    echo "❌ 错误: 项目目录不存在！"
    exit 1
}

echo "📥 拉取最新代码..."
git fetch origin
git reset --hard origin/master
git clean -fd

NEW_COMMIT=\$(git rev-parse HEAD)
echo "✅ 代码已更新: \$NEW_COMMIT"
echo ""

# 检查环境变量
if [ ! -f .env.production ]; then
    echo "❌ 错误: .env.production 文件不存在！"
    exit 1
fi

# 停止现有服务
echo "🛑 停止现有服务..."
docker compose -f docker-compose.production.yml down --timeout 30 || true

# 构建并启动
echo ""
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
echo "🚀 启动所有服务..."
docker compose --env-file .env.production \
    -f docker-compose.production.yml \
    up -d

echo ""
echo "⏳ 等待服务启动（60秒）..."
sleep 60

# 健康检查
echo ""
echo "🏥 执行健康检查..."
FAILED=0

for port in 8000 8080 3001; do
    if curl -f -s http://127.0.0.1:\$port/healthz > /dev/null 2>&1 || \
       curl -f -s http://127.0.0.1:\$port > /dev/null 2>&1; then
        echo "✅ 服务端口 \$port 健康检查通过"
    else
        echo "❌ 服务端口 \$port 健康检查失败"
        FAILED=1
    fi
done

# 显示服务状态
echo ""
echo "📊 服务状态:"
docker compose -f docker-compose.production.yml ps

if [ \$FAILED -eq 1 ]; then
    echo ""
    echo "⚠️  部分服务健康检查失败"
    exit 1
fi

echo ""
echo "===================================="
echo "✅ 部署成功！"
echo "===================================="
DEPLOY_SCRIPT

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}====================================${NC}"
    echo -e "${GREEN}✅ 部署完成！${NC}"
    echo -e "${GREEN}====================================${NC}"
    echo ""
    echo "部署信息:"
    echo "  服务器: $DEPLOY_USER@$DEPLOY_HOST"
    echo "  版本: $COMMIT_SHA"
    echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
else
    echo ""
    echo -e "${RED}====================================${NC}"
    echo -e "${RED}❌ 部署失败！${NC}"
    echo -e "${RED}====================================${NC}"
    exit 1
fi

