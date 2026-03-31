@echo off
title TORQ - Local Server
echo ========================================
echo    TORQ - Mechanical Engineering AI
echo ========================================
echo.
echo Starting local Streamlit server...
echo This will run TORQ on your local machine
echo.

REM Change to the directory where this bat file is located
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if streamlit is installed
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo Installing Streamlit and dependencies...
    pip install -r requirements.txt
)

echo.
echo Starting TORQ on http://localhost:8501
echo Press Ctrl+C to stop the server
echo.

REM Start Streamlit and automatically open browser
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --browser.gatherUsageStats false

pause