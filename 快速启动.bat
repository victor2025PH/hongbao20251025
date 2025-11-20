@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo =========================================
echo 全自动测试系统
echo =========================================
echo.

echo [1/3] 自动修复常见错误...
python auto_fix_common_errors.py
echo.

echo [2/3] 启动全自动测试...
echo 注意: 测试将在后台运行，服务会自动启动
echo 按 Ctrl+C 可以停止测试
echo.

python auto_test.py

echo.
echo 测试完成！
pause

