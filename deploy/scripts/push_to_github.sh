#!/bin/bash
# 推送代码到 GitHub 仓库

set -e

REPO_URL="https://github.com/victor2025PH/hongbao20251025.git"

echo "📤 开始推送代码到 GitHub..."
echo "仓库地址: $REPO_URL"
echo ""

# 检查是否在项目根目录
if [ ! -f "app.py" ] && [ ! -f "requirements.txt" ]; then
    echo "❌ 错误: 未找到项目文件，请确保在项目根目录执行此脚本"
    exit 1
fi

# 检查 Git 是否已初始化
if [ ! -d ".git" ]; then
    echo "📦 初始化 Git 仓库..."
    git init
    echo "✅ Git 仓库初始化完成"
else
    echo "✅ Git 仓库已存在"
fi
echo ""

# 检查远程仓库
if git remote get-url origin > /dev/null 2>&1; then
    CURRENT_URL=$(git remote get-url origin)
    echo "当前远程仓库: $CURRENT_URL"
    read -p "是否更新为新的仓库地址? (y/n): " update_remote
    if [ "$update_remote" = "y" ]; then
        git remote set-url origin $REPO_URL
        echo "✅ 远程仓库地址已更新"
    fi
else
    echo "🔗 添加远程仓库..."
    git remote add origin $REPO_URL
    echo "✅ 远程仓库已添加"
fi
echo ""

# 检查 .gitignore
if [ ! -f ".gitignore" ]; then
    echo "📝 创建 .gitignore 文件..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/
.venv/
venv/
env/
ENV/

# Node.js
node_modules/
npm-debug.log
.next/
.nuxt/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# 测试
.pytest_cache/
.mypy_cache/
.coverage
htmlcov/
*.sqlite
test_*.sqlite

# 日志
*.log
logs/

# 临时文件
*.tmp
*.bak
.DS_Store

# 环境变量和密钥
.env
.env.*
.env.local
secrets/
*.pem
*.key
service_account.json

# 导出文件
exports/
backups/

# 数据库文件
*.sqlite
data.sqlite
runtime.sqlite

# 其他
*.xlsx
*.csv
*.diff
*.patch
EOF
    echo "✅ .gitignore 已创建"
else
    echo "✅ .gitignore 已存在"
fi
echo ""

# 添加所有文件
echo "📦 添加文件到 Git..."
git add .
echo "✅ 文件已添加"
echo ""

# 检查是否有变更
if git diff --cached --quiet && git diff --quiet; then
    echo "ℹ️  没有变更需要提交"
    read -p "是否强制推送? (y/n): " force_push
    if [ "$force_push" = "y" ]; then
        echo "🚀 强制推送到 GitHub..."
        git push -u origin main --force || git push -u origin master --force
        echo "✅ 代码已推送"
    else
        echo "⏭️  跳过推送"
    fi
else
    # 提交
    echo "💾 提交变更..."
    read -p "请输入提交信息 (默认: Initial commit): " commit_msg
    commit_msg=${commit_msg:-"Initial commit"}
    git commit -m "$commit_msg"
    echo "✅ 变更已提交"
    echo ""

    # 推送到 GitHub
    echo "🚀 推送到 GitHub..."
    echo "⚠️  如果是第一次推送，可能需要输入 GitHub 用户名和密码/令牌"
    echo ""
    
    # 尝试推送到 main 分支，如果失败则尝试 master
    if git push -u origin main 2>/dev/null; then
        echo "✅ 代码已推送到 main 分支"
    elif git push -u origin master 2>/dev/null; then
        echo "✅ 代码已推送到 master 分支"
    else
        echo "❌ 推送失败，请检查："
        echo "   1. GitHub 用户名和密码/个人访问令牌"
        echo "   2. 仓库权限"
        echo "   3. 网络连接"
        echo ""
        echo "如果使用 HTTPS，可能需要使用个人访问令牌（Personal Access Token）"
        echo "生成地址: https://github.com/settings/tokens"
        exit 1
    fi
fi

echo ""
echo "✅ 代码推送完成！"
echo ""
echo "📋 仓库地址: https://github.com/victor2025PH/hongbao20251025"
echo ""
echo "下一步: 在服务器上克隆代码"
echo "  cd /opt/redpacket"
echo "  git clone https://github.com/victor2025PH/hongbao20251025.git ."

