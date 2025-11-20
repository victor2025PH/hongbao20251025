# 重新构建前端容器的 PowerShell 脚本

Write-Host "=== 重新构建前端容器 ===" -ForegroundColor Cyan

# 1. 停止并删除前端容器
Write-Host "停止并删除前端容器..." -ForegroundColor Yellow
docker compose stop frontend
docker compose rm -f frontend

# 2. 重新构建前端镜像（不使用缓存）
Write-Host "重新构建前端镜像（不使用缓存）..." -ForegroundColor Yellow
docker compose build --no-cache frontend

# 3. 启动前端容器
Write-Host "启动前端容器..." -ForegroundColor Yellow
docker compose up -d frontend

# 4. 等待服务启动
Write-Host "等待前端服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

# 5. 检查服务状态
Write-Host "`n=== 服务状态 ===" -ForegroundColor Cyan
docker compose ps frontend

# 6. 查看日志
Write-Host "`n=== 前端服务日志（最后 50 行）===" -ForegroundColor Cyan
docker compose logs --tail=50 frontend

Write-Host "`n完成！前端容器已重新构建并启动。" -ForegroundColor Green

