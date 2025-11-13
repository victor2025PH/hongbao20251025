#!/bin/bash
# 修复已存在目录的问题
# 使用方法: bash deploy/fix_existing_dir.sh

set -e

PROJECT_DIR="/opt/redpacket"
GIT_REPO="https://github.com/victor2025PH/hongbao20251025.git"

echo "🔧 修复已存在的目录问题..."
echo ""

# 检查目录是否存在
if [ -d "$PROJECT_DIR" ]; then
    echo "📁 目录 $PROJECT_DIR 已存在"
    
    cd "$PROJECT_DIR"
    
    # 检查是否是 Git 仓库
    if [ -d ".git" ]; then
        echo "✅ 检测到 Git 仓库，更新代码..."
        git fetch origin
        git reset --hard origin/master 2>/dev/null || git reset --hard origin/main 2>/dev/null
        echo "✅ 代码已更新"
    else
        echo "⚠️  目录存在但不是 Git 仓库"
        echo "   选项 1: 删除目录并重新克隆（推荐）"
        echo "   选项 2: 备份现有内容后重新克隆"
        echo ""
        read -p "选择操作 (1=删除并重新克隆, 2=备份后重新克隆): " choice
        
        if [ "$choice" = "1" ]; then
            echo "🗑️  删除现有目录..."
            cd /
            sudo rm -rf "$PROJECT_DIR"
            sudo mkdir -p "$PROJECT_DIR"
            sudo chown $USER:$USER "$PROJECT_DIR"
            cd "$PROJECT_DIR"
            echo "📥 克隆代码..."
            git clone "$GIT_REPO" .
            echo "✅ 代码已克隆"
        elif [ "$choice" = "2" ]; then
            BACKUP_DIR="${PROJECT_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
            echo "📦 备份到: $BACKUP_DIR"
            sudo mv "$PROJECT_DIR" "$BACKUP_DIR"
            sudo mkdir -p "$PROJECT_DIR"
            sudo chown $USER:$USER "$PROJECT_DIR"
            cd "$PROJECT_DIR"
            echo "📥 克隆代码..."
            git clone "$GIT_REPO" .
            echo "✅ 代码已克隆"
            echo "📝 备份位置: $BACKUP_DIR"
        else
            echo "❌ 无效选择"
            exit 1
        fi
    fi
else
    echo "📁 创建项目目录..."
    sudo mkdir -p "$PROJECT_DIR"
    sudo chown $USER:$USER "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    echo "📥 克隆代码..."
    git clone "$GIT_REPO" .
    echo "✅ 代码已克隆"
fi

echo ""
echo "✅ 完成！现在可以运行部署脚本了："
echo "   cd $PROJECT_DIR"
echo "   sudo bash deploy/auto_deploy.sh"

