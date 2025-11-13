#!/bin/bash
# 远程服务器部署脚本 - 直接在服务器上运行
# 使用方法: bash deploy/remote_deploy.sh

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 项目配置
PROJECT_DIR="/opt/redpacket"
GIT_REPO="https://github.com/victor2025PH/hongbao20251025.git"

log_info "=========================================="
log_info "   红包系统 - 远程服务器部署"
log_info "=========================================="
echo ""

# 检查是否为 root
if [ "$EUID" -ne 0 ]; then
    log_error "请使用 sudo 运行此脚本"
    exit 1
fi

# 步骤 1: 创建项目目录
log_info "========== 步骤 1: 创建项目目录 =========="
mkdir -p "$PROJECT_DIR"
chown $SUDO_USER:$SUDO_USER "$PROJECT_DIR"
log_success "项目目录已创建: $PROJECT_DIR"
echo ""

# 步骤 2: 克隆代码
log_info "========== 步骤 2: 克隆代码 =========="
cd "$PROJECT_DIR"

if [ -d ".git" ]; then
    log_info "检测到现有 Git 仓库，更新代码..."
    git fetch origin
    git reset --hard origin/master 2>/dev/null || git reset --hard origin/main 2>/dev/null
    log_success "代码已更新"
else
    log_info "克隆代码仓库..."
    git clone "$GIT_REPO" .
    chown -R $SUDO_USER:$SUDO_USER .
    log_success "代码已克隆"
fi
echo ""

# 步骤 3: 运行自动部署脚本
log_info "========== 步骤 3: 运行自动部署脚本 =========="
if [ -f "deploy/auto_deploy.sh" ]; then
    log_info "找到自动部署脚本，开始执行..."
    bash deploy/auto_deploy.sh
else
    log_error "未找到 deploy/auto_deploy.sh 文件"
    log_info "尝试使用 Docker Compose 部署脚本..."
    if [ -f "deploy/scripts/deploy_docker_compose.sh" ]; then
        bash deploy/scripts/deploy_docker_compose.sh
    else
        log_error "未找到部署脚本，请手动部署"
        exit 1
    fi
fi

log_success "✅ 部署完成！"

