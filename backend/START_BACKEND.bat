@echo off
title Backend - AI Deepfake Verifier

echo ========================================
echo  Starting Backend Server
echo ========================================
echo.

cd /d "%~dp0"

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run RECREATE_VENV.bat first
    echo.
    pause
    exit /b 1
)

REM Activate venv and start server
call venv\Scripts\activate
echo Virtual environment activated!
echo.
echo Starting AI Deepfake Truth Verifier API...
echo Please wait for model to load (10-30 seconds)...
echo.
python -m app.main

pause
