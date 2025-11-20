# 检查服务器上的 .env.production 文件

$bashPath = "C:\Program Files\Git\bin\bash.exe"
$server = "ubuntu@165.154.233.55"
$projectDir = "/opt/redpacket"

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "🔍 检查服务器上的 .env.production 文件" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# 创建临时脚本
$scriptContent = @"
ssh -o StrictHostKeyChecking=no $server << 'REMOTE_SCRIPT'
cd $projectDir
echo "=== 检查 .env.production 文件 ==="
echo ""

if [ -f .env.production ]; then
    echo "✅ 文件存在"
    echo ""
    echo "文件信息:"
    ls -lh .env.production
    echo ""
    echo "文件大小:"
    du -h .env.production
    echo ""
    echo "文件权限:"
    stat -c "Permissions: %a" .env.production 2>/dev/null || ls -l .env.production | awk '{print \$1}'
    echo ""
    echo "文件前5行（隐藏敏感内容）:"
    head -5 .env.production | sed 's/=.*/=***/g' || echo "无法读取文件内容"
else
    echo "❌ 文件不存在"
    echo ""
    echo "检查是否有模板文件:"
    ls -la .env* 2>/dev/null || echo "没有找到 .env 相关文件"
    echo ""
    echo "检查 backups 目录是否有备份:"
    if [ -d backups ]; then
        ls -la backups/*.env* 2>/dev/null || echo "backups 目录中没有 .env 文件备份"
    else
        echo "backups 目录不存在"
    fi
fi
REMOTE_SCRIPT
"@

# 保存到临时文件
$tempScript = [System.IO.Path]::GetTempFileName() + ".sh"
$scriptContent | Out-File -FilePath $tempScript -Encoding UTF8 -NoNewline

try {
    # 执行脚本
    & $bashPath $tempScript
} finally {
    # 清理临时文件
    Remove-Item $tempScript -ErrorAction SilentlyContinue
}

Write-Host ""

