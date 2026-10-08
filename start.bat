@echo off
cd /d "%~dp0"

set "PY=.venv\Scripts\python.exe"

"%PY%" -c "import gradio" 2>nul
if errorlevel 1 (
    echo Installing gradio into the virtual environment, please wait...
    "%PY%" -m pip install --quiet gradio
)

"%PY%" web_app.py

pause
