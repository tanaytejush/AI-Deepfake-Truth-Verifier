@echo off
echo ========================================
echo AI Deepfake Truth Verifier - Launcher
echo ========================================
echo.

echo [1/2] Starting Backend Server...
start cmd /k "cd backend && venv\Scripts\activate && python -m app.main"

timeout /t 3 /nobreak > nul

echo [2/2] Starting Frontend Server...
start cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo Both servers are starting...
echo ========================================
echo.
echo Backend will be at: http://localhost:8000
echo Frontend will be at: http://localhost:5173
echo.
echo Wait 10-20 seconds for model to load, then open:
echo http://localhost:5173
echo.
echo Press any key to exit this window...
pause > nul
