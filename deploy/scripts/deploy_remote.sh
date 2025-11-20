#!/usr/bin/env bash
# 远程部署触发器
# 使用方法: bash deploy/scripts/deploy_remote.sh [分支名]

set -euo pipefail

# === 配置变量（可通过环境变量覆盖） ===
SERVER_USER="${DEPLOY_USER:-ubuntu}"                    # 远程服务器用户名
SERVER_IP="${DEPLOY_HOST:-165.154.233.55}"             # 远程服务器 IP
PROJECT_DIR="${DEPLOY_PATH:-/opt/redpacket}"           # 远程项目目录
BRANCH="${1:-${DEPLOY_BRANCH:-master}}"                # 要部署的分支
SSH_KEY="${SSH_KEY:-~/.ssh/id_rsa}"                    # SSH 私钥路径
SSH_PORT="${DEPLOY_PORT:-22}"                          # SSH 端口

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}====================================${NC}"
echo -e "${BLUE}🚀 开始远程部署${NC}"
echo -e "${BLUE}====================================${NC}"
echo ""
echo "部署配置:"
echo "  服务器: $SERVER_USER@$SERVER_IP:$SSH_PORT"
echo "  项目目录: $PROJECT_DIR"
echo "  分支: $BRANCH"
echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 检查 SSH 密钥是否存在
if [ ! -f "$SSH_KEY" ]; then
    echo -e "${YELLOW}⚠️  SSH 密钥不存在: $SSH_KEY${NC}"
    echo "尝试使用默认密钥..."
    SSH_KEY="~/.ssh/id_rsa"
fi

# 测试 SSH 连接
echo -e "${YELLOW}🔍 测试 SSH 连接...${NC}"
if ssh -i "$SSH_KEY" \
    -p "$SSH_PORT" \
    -o ConnectTimeout=5 \
    -o StrictHostKeyChecking=no \
    -o BatchMode=yes \
    "$SERVER_USER@$SERVER_IP" "echo 'SSH 连接成功'" 2>/dev/null; then
    echo -e "${GREEN}✅ SSH 连接成功${NC}"
else
    echo -e "${RED}❌ SSH 连接失败${NC}"
    echo ""
    echo "请检查:"
    echo "  1. 服务器 IP 是否正确: $SERVER_IP"
    echo "  2. SSH 用户名是否正确: $SERVER_USER"
    echo "  3. SSH 密钥是否正确: $SSH_KEY"
    echo "  4. 服务器是否允许 SSH 连接"
    exit 1
fi
echo ""

# 检查远程部署脚本是否存在
echo -e "${YELLOW}🔍 检查远程部署脚本...${NC}"
if ssh -i "$SSH_KEY" \
    -p "$SSH_PORT" \
    -o StrictHostKeyChecking=no \
    "$SERVER_USER@$SERVER_IP" "test -f $PROJECT_DIR/deploy/scripts/deploy.sh" 2>/dev/null; then
    echo -e "${GREEN}✅ 远程部署脚本存在${NC}"
else
    echo -e "${YELLOW}⚠️  远程部署脚本不存在，将创建...${NC}"
    
    # 上传部署脚本
    if [ -f "deploy/scripts/deploy.sh" ]; then
        echo "上传部署脚本到服务器..."
        scp -i "$SSH_KEY" \
            -P "$SSH_PORT" \
            -o StrictHostKeyChecking=no \
            "deploy/scripts/deploy.sh" \
            "$SERVER_USER@$SERVER_IP:$PROJECT_DIR/deploy/scripts/deploy.sh"
        
        ssh -i "$SSH_KEY" \
            -p "$SSH_PORT" \
            -o StrictHostKeyChecking=no \
            "$SERVER_USER@$SERVER_IP" "chmod +x $PROJECT_DIR/deploy/scripts/deploy.sh"
        
        echo -e "${GREEN}✅ 远程部署脚本已创建${NC}"
    else
        echo -e "${RED}❌ 本地部署脚本不存在: deploy/scripts/deploy.sh${NC}"
        echo "请先创建远程部署脚本"
        exit 1
    fi
fi
echo ""

# 执行远程部署
echo -e "${YELLOW}🚀 执行远程部署...${NC}"
echo ""

ssh -i "$SSH_KEY" \
    -p "$SSH_PORT" \
    -o StrictHostKeyChecking=no \
    "$SERVER_USER@$SERVER_IP" \
    "cd $PROJECT_DIR && bash deploy/scripts/deploy.sh $BRANCH"

DEPLOY_EXIT_CODE=$?

echo ""

if [ $DEPLOY_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}====================================${NC}"
    echo -e "${GREEN}✅ 远程部署完成！${NC}"
    echo -e "${GREEN}====================================${NC}"
    echo ""
    echo "部署信息:"
    echo "  服务器: $SERVER_USER@$SERVER_IP"
    echo "  分支: $BRANCH"
    echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
else
    echo -e "${RED}====================================${NC}"
    echo -e "${RED}❌ 远程部署失败！${NC}"
    echo -e "${RED}====================================${NC}"
    echo ""
    echo "退出代码: $DEPLOY_EXIT_CODE"
    echo "请检查远程服务器日志: $PROJECT_DIR/logs/deploy.log"
    exit $DEPLOY_EXIT_CODE
fi

