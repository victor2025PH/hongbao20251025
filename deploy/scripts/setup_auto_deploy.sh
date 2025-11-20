#!/bin/bash
# 设置自动化部署环境
# 使用方法: bash deploy/scripts/setup_auto_deploy.sh

set -e

echo "===================================="
echo "🔧 设置自动化部署环境"
echo "===================================="
echo ""

# 步骤 1: 生成 SSH 密钥（如果不存在）
echo "步骤 1: 检查 SSH 密钥..."
SSH_KEY="$HOME/.ssh/deploy_key"
if [ ! -f "$SSH_KEY" ]; then
    echo "生成新的 SSH 密钥..."
    ssh-keygen -t rsa -b 4096 -C "deploy@redpacket" -f "$SSH_KEY" -N ""
    echo "✅ SSH 密钥已生成: $SSH_KEY"
else
    echo "✅ SSH 密钥已存在: $SSH_KEY"
fi
echo ""

# 步骤 2: 读取服务器信息
echo "步骤 2: 配置服务器信息..."
read -p "请输入服务器 IP 地址: " DEPLOY_HOST
read -p "请输入 SSH 用户名 (默认: ubuntu): " DEPLOY_USER
DEPLOY_USER=${DEPLOY_USER:-ubuntu}
read -p "请输入 SSH 端口 (默认: 22): " DEPLOY_PORT
DEPLOY_PORT=${DEPLOY_PORT:-22}
read -p "请输入部署路径 (默认: /opt/redpacket): " DEPLOY_PATH
DEPLOY_PATH=${DEPLOY_PATH:-/opt/redpacket}
echo ""

# 步骤 3: 复制公钥到服务器
echo "步骤 3: 配置服务器 SSH 密钥..."
echo "请确保可以 SSH 连接到服务器..."
read -p "是否现在配置? (y/N): " confirm

if [[ "$confirm" =~ ^[Yy]$ ]]; then
    echo "复制公钥到服务器..."
    ssh-copy-id -i "$SSH_KEY.pub" -p "$DEPLOY_PORT" "$DEPLOY_USER@$DEPLOY_HOST" || {
        echo "手动配置方法:"
        echo "1. 查看公钥: cat $SSH_KEY.pub"
        echo "2. 在服务器上执行:"
        echo "   mkdir -p ~/.ssh"
        echo "   echo '你的公钥' >> ~/.ssh/authorized_keys"
        echo "   chmod 600 ~/.ssh/authorized_keys"
    }
fi
echo ""

# 步骤 4: 测试 SSH 连接
echo "步骤 4: 测试 SSH 连接..."
if ssh -i "$SSH_KEY" -p "$DEPLOY_PORT" -o ConnectTimeout=5 \
    -o StrictHostKeyChecking=no \
    "$DEPLOY_USER@$DEPLOY_HOST" "echo 'SSH 连接成功'" &> /dev/null; then
    echo "✅ SSH 连接测试成功"
else
    echo "❌ SSH 连接测试失败，请检查配置"
    exit 1
fi
echo ""

# 步骤 5: 在服务器上创建必要的目录
echo "步骤 5: 在服务器上创建必要的目录..."
ssh -i "$SSH_KEY" -p "$DEPLOY_PORT" "$DEPLOY_USER@$DEPLOY_HOST" << SERVER_SETUP
set -e

# 创建项目目录
sudo mkdir -p "$DEPLOY_PATH"
sudo chown -R \$USER:\$USER "$DEPLOY_PATH"

# 创建日志目录
mkdir -p "$DEPLOY_PATH/logs"
chmod 755 "$DEPLOY_PATH/logs"

# 如果项目不存在，克隆代码
if [ ! -d "$DEPLOY_PATH/.git" ]; then
    read -p "项目目录不存在，是否克隆代码? (y/N): " clone_confirm
    if [[ "\$clone_confirm" =~ ^[Yy]$ ]]; then
        read -p "请输入 Git 仓库地址: " GIT_REPO
        git clone "\$GIT_REPO" "$DEPLOY_PATH"
    fi
fi

echo "✅ 服务器目录已准备"
SERVER_SETUP

# 步骤 6: 创建配置文件
echo ""
echo "步骤 6: 创建配置文件..."
cat > .env.deploy << EOF
# 自动化部署配置
DEPLOY_HOST=$DEPLOY_HOST
DEPLOY_USER=$DEPLOY_USER
DEPLOY_PORT=$DEPLOY_PORT
DEPLOY_PATH=$DEPLOY_PATH
SSH_KEY=$SSH_KEY
EOF

echo "✅ 配置文件已创建: .env.deploy"
echo ""

# 步骤 7: 配置 GitHub Secrets（提示）
echo "步骤 7: GitHub Actions 配置提示"
echo ""
echo "如果使用 GitHub Actions，请在仓库设置中添加以下 Secrets:"
echo ""
echo "  DEPLOY_HOST=$DEPLOY_HOST"
echo "  DEPLOY_USER=$DEPLOY_USER"
echo "  DEPLOY_PORT=$DEPLOY_PORT"
echo "  DEPLOY_PATH=$DEPLOY_PATH"
echo "  DEPLOY_SSH_KEY=$(cat $SSH_KEY)"
echo ""
echo "配置路径:"
echo "  Settings → Secrets and variables → Actions → New repository secret"
echo ""

# 步骤 8: 测试部署
read -p "是否现在测试部署? (y/N): " test_confirm
if [[ "$test_confirm" =~ ^[Yy]$ ]]; then
    echo ""
    echo "执行测试部署..."
    bash deploy/scripts/auto_deploy_pipeline.sh "$DEPLOY_HOST" "$DEPLOY_USER"
fi

echo ""
echo "===================================="
echo "✅ 自动化部署环境设置完成！"
echo "===================================="
echo ""
echo "下一步:"
echo "  1. 使用 GitHub Actions: 推送代码到 master 分支"
echo "  2. 使用本地脚本: bash deploy/scripts/auto_deploy_pipeline.sh"
echo "  3. 使用 Webhook: 配置 GitHub Webhook 并启动接收器"
echo ""

