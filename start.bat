@echo off
title Audio to Text Transcription
cd /d "%~dp0"

set "PY=.venv\Scripts\python.exe"

if exist "%PY%" goto :have_venv

echo Creating virtual environment, first run only...
where py >nul 2>&1
if not errorlevel 1 py -3.12 -m venv .venv 2>nul
if not exist "%PY%" (
    where python >nul 2>&1
    if not errorlevel 1 python -m venv .venv
)
if not exist "%PY%" (
    echo Python was not found. Install Python 3.12 from https://www.python.org/downloads/
    echo and tick "Add python.exe to PATH" during setup, then run start.bat again.
    pause
    exit /b 1
)

:have_venv
"%PY%" -c "import torch" >nul 2>&1
if errorlevel 1 (
    where nvidia-smi >nul 2>&1
    if errorlevel 1 (
        echo No NVIDIA GPU detected - installing CPU version of PyTorch. Transcription will be slow.
        "%PY%" -m pip install torch
    ) else (
        echo Installing PyTorch with GPU support. This is a large download, about 3 GB...
        "%PY%" -m pip install torch --index-url https://download.pytorch.org/whl/cu130
    )
    if errorlevel 1 goto :install_failed
)

"%PY%" -c "import transformers, accelerate, gradio" >nul 2>&1
if errorlevel 1 (
    echo Installing the remaining packages...
    "%PY%" -m pip install -r requirements.txt
    if errorlevel 1 goto :install_failed
)

"%PY%" web_app.py

pause
exit /b 0

:install_failed
echo Package installation failed. Check your internet connection and run start.bat again.
pause
exit /b 1
