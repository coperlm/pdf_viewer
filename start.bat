@echo off
echo 启动PDF阅读器...
cd /d "%~dp0"
python main.py %1
pause
