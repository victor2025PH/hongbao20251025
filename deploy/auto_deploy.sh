#!/bin/bash
# 全自动部署脚本 - 红包系统
# 使用方法: bash deploy/auto_deploy.sh

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_DIR="/opt/redpacket"
GIT_REPO="https://github.com/victor2025PH/hongbao20251025.git"
BACKUP_DIR="/opt/redpacket/backups"

# 日志函数
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

# 检查命令是否存在
check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# 检查是否为 root 用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用 root 用户或 sudo 运行此脚本"
        exit 1
    fi
}

# 步骤 1: 检查系统环境
step1_check_environment() {
    log_info "========== 步骤 1: 检查系统环境 =========="
    
    # 检查操作系统
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        log_info "操作系统: $PRETTY_NAME"
    else
        log_error "无法检测操作系统"
        exit 1
    fi
    
    # 检查系统架构
    ARCH=$(uname -m)
    log_info "系统架构: $ARCH"
    
    # 检查内存
    MEM_TOTAL=$(free -m | awk '/^Mem:/{print $2}')
    log_info "总内存: ${MEM_TOTAL}MB"
    if [ "$MEM_TOTAL" -lt 2048 ]; then
        log_warning "内存少于 2GB，可能影响性能"
    fi
    
    # 检查磁盘空间
    DISK_AVAIL=$(df -h / | awk 'NR==2 {print $4}')
    log_info "可用磁盘空间: $DISK_AVAIL"
    
    # 检查端口占用
    log_info "检查端口占用情况..."
    for port in 8000 3001 5432 6379; do
        if netstat -tuln 2>/dev/null | grep -q ":$port "; then
            log_warning "端口 $port 已被占用"
        else
            log_success "端口 $port 可用"
        fi
    done
    
    log_success "环境检查完成"
    echo ""
}

# 步骤 2: 安装 Docker
step2_install_docker() {
    log_info "========== 步骤 2: 安装 Docker =========="
    
    if check_command docker; then
        DOCKER_VERSION=$(docker --version)
        log_success "Docker 已安装: $DOCKER_VERSION"
    else
        log_info "开始安装 Docker..."
        
        # 更新包索引
        apt-get update -qq
        
        # 安装依赖
        apt-get install -y -qq \
            apt-transport-https \
            ca-certificates \
            curl \
            gnupg \
            lsb-release
        
        # 添加 Docker 官方 GPG 密钥
        install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        chmod a+r /etc/apt/keyrings/docker.gpg
        
        # 设置 Docker 仓库
        echo \
          "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
          $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
          tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # 安装 Docker Engine
        apt-get update -qq
        apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        
        # 启动 Docker 服务
        systemctl start docker
        systemctl enable docker
        
        log_success "Docker 安装完成"
    fi
    
    echo ""
}

# 步骤 3: 安装 Docker Compose
step3_install_docker_compose() {
    log_info "========== 步骤 3: 安装 Docker Compose =========="
    
    if check_command docker-compose || docker compose version &> /dev/null; then
        if docker compose version &> /dev/null; then
            COMPOSE_VERSION=$(docker compose version)
            log_success "Docker Compose 已安装: $COMPOSE_VERSION"
        else
            COMPOSE_VERSION=$(docker-compose --version)
            log_success "Docker Compose 已安装: $COMPOSE_VERSION"
        fi
    else
        log_info "Docker Compose 已包含在 Docker 安装中，检查中..."
        if docker compose version &> /dev/null; then
            log_success "Docker Compose 可用"
        else
            log_error "Docker Compose 不可用，请检查 Docker 安装"
            exit 1
        fi
    fi
    
    echo ""
}

# 步骤 4: 创建项目目录
step4_create_project_dir() {
    log_info "========== 步骤 4: 创建项目目录 =========="
    
    if [ ! -d "$PROJECT_DIR" ]; then
        mkdir -p "$PROJECT_DIR"
        log_success "创建项目目录: $PROJECT_DIR"
    else
        log_info "项目目录已存在: $PROJECT_DIR"
    fi
    
    # 创建备份目录
    mkdir -p "$BACKUP_DIR"
    log_success "创建备份目录: $BACKUP_DIR"
    
    echo ""
}

# 步骤 5: 克隆或更新代码
step5_clone_code() {
    log_info "========== 步骤 5: 克隆/更新代码 =========="
    
    cd "$PROJECT_DIR"
    
    if [ -d ".git" ]; then
        log_info "检测到现有 Git 仓库，更新代码..."
        git fetch origin
        git reset --hard origin/master || git reset --hard origin/main
        log_success "代码已更新"
    else
        log_info "克隆代码仓库..."
        git clone "$GIT_REPO" .
        log_success "代码已克隆"
    fi
    
    echo ""
}

# 步骤 6: 配置环境变量
step6_configure_env() {
    log_info "========== 步骤 6: 配置环境变量 =========="
    
    cd "$PROJECT_DIR"
    
    if [ ! -f ".env.production" ]; then
        log_info "创建生产环境配置文件..."
        
        if [ -f ".env.production.example" ]; then
            cp .env.production.example .env.production
            log_success "已从示例文件创建 .env.production"
        else
            log_warning ".env.production.example 不存在，创建基础配置..."
            cat > .env.production << 'EOF'
# 生产环境配置
# 请修改以下配置为实际值

# 数据库配置
POSTGRES_DB=redpacket
POSTGRES_USER=redpacket
POSTGRES_PASSWORD=请修改为强密码

# Telegram Bot
BOT_TOKEN=请填入您的Bot Token

# 管理员配置
ADMIN_IDS=请填入您的Telegram ID

# JWT 密钥（使用 openssl rand -hex 32 生成）
MINIAPP_JWT_SECRET=请生成随机字符串
ADMIN_SESSION_SECRET=请生成随机字符串

# API 配置
API_BASE_URL=http://localhost:8000
EOF
            log_success "已创建基础 .env.production"
        fi
        
        log_warning "⚠️  请编辑 .env.production 文件，填入实际配置值"
        log_info "可以使用以下命令编辑:"
        log_info "  nano $PROJECT_DIR/.env.production"
        log_info ""
        log_info "必需配置项:"
        log_info "  - POSTGRES_PASSWORD: 数据库密码（至少16位）"
        log_info "  - BOT_TOKEN: Telegram Bot Token"
        log_info "  - ADMIN_IDS: 您的 Telegram ID"
        log_info "  - MINIAPP_JWT_SECRET: 运行 'openssl rand -hex 32' 生成"
        log_info "  - ADMIN_SESSION_SECRET: 运行 'openssl rand -hex 32' 生成"
        log_info ""
        
        read -p "是否现在编辑配置文件? (y/n): " edit_now
        if [ "$edit_now" = "y" ] || [ "$edit_now" = "Y" ]; then
            ${EDITOR:-nano} .env.production
        fi
    else
        log_info ".env.production 已存在，跳过创建"
    fi
    
    echo ""
}

# 步骤 7: 初始化数据库
step7_init_database() {
    log_info "========== 步骤 7: 初始化数据库 =========="
    
    cd "$PROJECT_DIR"
    
    log_info "数据库将在 Docker Compose 启动时自动初始化"
    log_info "如果使用外部数据库，请手动运行迁移脚本"
    
    echo ""
}

# 步骤 8: 构建和启动服务
step8_start_services() {
    log_info "========== 步骤 8: 构建和启动服务 =========="
    
    cd "$PROJECT_DIR"
    
    # 检查 docker-compose 文件
    if [ ! -f "docker-compose.production.yml" ]; then
        log_error "未找到 docker-compose.production.yml 文件"
        exit 1
    fi
    
    log_info "使用 Docker Compose 启动服务..."
    
    # 停止现有服务（如果有）
    docker compose -f docker-compose.production.yml down 2>/dev/null || true
    
    # 构建镜像
    log_info "构建 Docker 镜像（这可能需要几分钟）..."
    docker compose -f docker-compose.production.yml build
    
    # 启动服务
    log_info "启动服务..."
    docker compose -f docker-compose.production.yml up -d
    
    log_success "服务已启动"
    echo ""
}

# 步骤 9: 验证部署
step9_verify_deployment() {
    log_info "========== 步骤 9: 验证部署 =========="
    
    log_info "等待服务启动（30秒）..."
    sleep 30
    
    # 检查容器状态
    log_info "检查容器状态..."
    docker compose -f docker-compose.production.yml ps
    
    # 检查健康状态
    log_info "检查服务健康状态..."
    
    # 后端健康检查
    if curl -f -s http://localhost:8000/healthz > /dev/null; then
        log_success "后端服务 (8000) 运行正常"
    else
        log_warning "后端服务 (8000) 可能未就绪，请检查日志"
    fi
    
    # 前端健康检查
    if curl -f -s http://localhost:3001 > /dev/null; then
        log_success "前端服务 (3001) 运行正常"
    else
        log_warning "前端服务 (3001) 可能未就绪，请检查日志"
    fi
    
    echo ""
}

# 步骤 10: 显示部署信息
step10_show_info() {
    log_info "========== 步骤 10: 部署信息 =========="
    
    log_success "🎉 部署完成！"
    echo ""
    log_info "服务访问地址:"
    log_info "  - 后端 API: http://$(hostname -I | awk '{print $1}'):8000"
    log_info "  - 前端控制台: http://$(hostname -I | awk '{print $1}'):3001"
    log_info "  - 健康检查: http://$(hostname -I | awk '{print $1}'):8000/healthz"
    echo ""
    log_info "常用命令:"
    log_info "  - 查看服务状态: docker compose -f docker-compose.production.yml ps"
    log_info "  - 查看日志: docker compose -f docker-compose.production.yml logs -f"
    log_info "  - 停止服务: docker compose -f docker-compose.production.yml down"
    log_info "  - 重启服务: docker compose -f docker-compose.production.yml restart"
    echo ""
    log_info "配置文件位置:"
    log_info "  - 环境变量: $PROJECT_DIR/.env.production"
    log_info "  - Docker Compose: $PROJECT_DIR/docker-compose.production.yml"
    echo ""
    log_warning "⚠️  重要提示:"
    log_warning "  1. 请确保防火墙已开放端口 8000 和 3001"
    log_warning "  2. 如果使用域名，请配置 Nginx 反向代理和 SSL 证书"
    log_warning "  3. 定期备份数据库: $BACKUP_DIR"
    echo ""
}

# 主函数
main() {
    log_info "=========================================="
    log_info "   红包系统 - 全自动部署脚本"
    log_info "=========================================="
    echo ""
    
    # 检查 root 权限
    check_root
    
    # 执行部署步骤
    step1_check_environment
    step2_install_docker
    step3_install_docker_compose
    step4_create_project_dir
    step5_clone_code
    step6_configure_env
    step7_init_database
    step8_start_services
    step9_verify_deployment
    step10_show_info
    
    log_success "✅ 所有步骤完成！"
}

# 运行主函数
main

