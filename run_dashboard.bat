@echo off
echo ========================================
echo   BioSync Tele-Rescue Dashboard
echo   Healthcare Telemedicine Platform
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

echo.
echo Starting backend and dashboard...
echo.
python run_dashboard.py

if errorlevel 1 (
    echo.
    echo ERROR: Launcher exited unexpectedly.
    pause
    exit /b 1
)
