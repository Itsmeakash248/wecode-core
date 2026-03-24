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
echo Installing/updating dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Starting BioSync Tele-Rescue Dashboard...
echo.
echo The application will open in your default browser
echo Press Ctrl+C to stop the server
echo.

python -m streamlit run app.py --server.headless true --server.port 8501

echo.
echo Application stopped.
pause