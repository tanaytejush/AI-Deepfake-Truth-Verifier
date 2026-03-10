@echo off
title Fixing and Starting AI Deepfake Verifier

echo ========================================
echo  FIXING INSTALLATION ISSUES
echo ========================================
echo.

REM Fix Frontend - Reinstall Vite
echo [Step 1/3] Fixing Frontend (Installing Vite)...
echo This may take 1-2 minutes...
echo.
cd /d "%~dp0frontend"
call npm install
if errorlevel 1 (
    echo ERROR: Frontend installation failed!
    pause
    exit /b 1
)
echo ✓ Frontend fixed!
echo.

REM Check Backend Virtual Environment
echo [Step 2/3] Checking Backend...
cd /d "%~dp0backend"
if not exist "venv\" (
    echo Creating Python virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
) else (
    echo ✓ Backend venv exists!
)
echo.

REM Start Servers
echo [Step 3/3] Starting Servers...
echo.

echo Starting Backend Server...
start "Backend - AI Deepfake Verifier" cmd /k "cd /d "%~dp0backend" && venv\Scripts\activate && python -m app.main"

timeout /t 5 /nobreak > nul

echo Starting Frontend Server...
start "Frontend - AI Deepfake Verifier" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ========================================
echo  SERVERS STARTING!
echo ========================================
echo.
echo Two windows opened:
echo   1. Backend Server (loading model...)
echo   2. Frontend Server (building...)
echo.
echo WAIT 15-20 SECONDS for backend to load
echo Then open: http://localhost:5173
echo.
echo Press any key to close this window...
pause > nul
