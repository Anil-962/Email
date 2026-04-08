@echo off
echo Activating local virtual environment...
cd /d "%~dp0"
.\my_env\.venv\Scripts\python.exe test_api.py
pause
