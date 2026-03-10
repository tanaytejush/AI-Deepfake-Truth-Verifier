@echo off
title AI Deepfake Verifier - Launcher

echo ========================================
echo  AI Deepfake Truth Verifier
echo ========================================
echo.
echo Starting servers...
echo.

REM Start Backend
echo [1/2] Starting Backend Server...
start "Backend Server" cmd /k "cd /d "%~dp0backend" && venv\Scripts\activate && python -m app.main"

REM Wait for backend to initialize
timeout /t 5 /nobreak > nul

REM Start Frontend
echo [2/2] Starting Frontend Server...
start "Frontend Server" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ========================================
echo Servers are starting!
echo ========================================
echo.
echo Two windows will open:
echo   1. Backend Server (http://localhost:8000)
echo   2. Frontend Server (http://localhost:5173)
echo.
echo Wait 15-20 seconds for backend to load model
echo Then open: http://localhost:5173
echo.
echo Press any key to close this window...
pause > nul
