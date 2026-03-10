@echo off
title Recreating Backend Virtual Environment

echo ========================================
echo  Recreating Python Virtual Environment
echo ========================================
echo.
echo This will:
echo  1. Backup old venv
echo  2. Create new Windows-compatible venv
echo  3. Install all dependencies
echo.
echo This may take 2-3 minutes...
echo.

cd /d "%~dp0"

REM Backup old venv
if exist "venv\" (
    echo Renaming old venv to venv_old...
    rename venv venv_old
)

REM Create new venv
echo.
echo Creating new virtual environment...
python -m venv venv

if errorlevel 1 (
    echo ERROR: Failed to create virtual environment!
    echo Make sure Python is installed and in PATH
    pause
    exit /b 1
)

REM Activate and install dependencies
echo.
echo Installing dependencies...
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  SUCCESS! Virtual environment ready!
echo ========================================
echo.
echo You can now run the backend with:
echo   venv\Scripts\activate
echo   python -m app.main
echo.
echo Or just run: START_BACKEND.bat
echo.
pause
