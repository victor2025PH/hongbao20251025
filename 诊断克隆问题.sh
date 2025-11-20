#!/bin/bash
# 診斷 Git 克隆問題

cd /opt/redpacket

echo "===================================="
echo "🔍 診斷 Git 克隆問題"
echo "===================================="
echo ""

# 檢查當前目錄內容
echo "📂 當前目錄內容："
ls -la
echo ""

# 檢查 Git 狀態
echo "📊 Git 狀態："
git status
echo ""

# 檢查分支
echo "🌿 Git 分支："
git branch -a
echo ""

# 檢查遠程倉庫
echo "🌐 遠程倉庫："
git remote -v
echo ""

# 檢查是否有 .gitignore 忽略文件
echo "🚫 .gitignore 內容："
if [ -f .gitignore ]; then
    cat .gitignore
else
    echo "  .gitignore 不存在"
fi
echo ""

# 檢查所有文件（包括隱藏文件）
echo "📋 所有文件和目錄（詳細）："
find . -maxdepth 2 -type f -o -type d | head -30
echo ""

# 檢查是否在正確的分支
echo "📍 當前分支："
git branch --show-current
echo ""

# 嘗試列出所有文件
echo "📄 Git 倉庫中的所有文件："
git ls-files | head -50
echo ""

echo "===================================="
echo "✅ 診斷完成"
echo "===================================="
echo ""

