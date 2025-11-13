@echo off
cd /d "E:\002-工作文件\重要程序\红包系统机器人\037重新开发新功能"
python -m uvicorn web_admin.main:app --host 0.0.0.0 --port 8000 --reload
pause
