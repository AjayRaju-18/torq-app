@echo off
color 0A
title TORQ Launcher - Mechanical Engineering AI Assistant

:menu
cls
echo ========================================
echo    🤖 TORQ LAUNCHER 🤖
echo    Mechanical Engineering AI Assistant  
echo ========================================
echo.
echo Choose how to open TORQ:
echo.
echo [1] Open Web App (Streamlit Cloud) - RECOMMENDED
echo [2] Run Local Server (localhost:8501)
echo [3] Open on Phone/Network (0.0.0.0:8501)
echo [4] Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto web
if "%choice%"=="2" goto local
if "%choice%"=="3" goto network
if "%choice%"=="4" goto exit
echo Invalid choice. Please try again.
timeout /t 2 >nul
goto menu

:web
cls
echo Opening TORQ Web App from Streamlit Cloud...
echo.
echo ✅ This is the RECOMMENDED option
echo ✅ Always up-to-date
echo ✅ No local setup required
echo ✅ Works on any device
echo.
start "" "https://torq-app-dbd36yhetgbc7epzhitxhd.streamlit.app/"
echo Web app should open in your browser shortly!
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:local
cls
echo Starting TORQ Local Server...
echo.
cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed
    echo Please install Python first
    pause
    goto menu
)

python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo ✅ Starting TORQ on http://localhost:8501
echo ✅ Local server - works offline
echo.
echo Press Ctrl+C to stop server, then any key to return to menu
streamlit run app.py --server.port 8501 --browser.gatherUsageStats false
echo.
pause
goto menu

:network
cls
echo Starting TORQ Network Server...
echo.
cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed
    pause
    goto menu
)

echo ✅ Starting TORQ on all network interfaces
echo ✅ Access from phone/other devices on same network
echo.
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /i "IPv4"') do (
    set ip=%%i
    set ip=!ip: =!
    echo 📱 Access from phone: http://!ip!:8501
)
echo 💻 Access locally: http://localhost:8501
echo.
echo Press Ctrl+C to stop server, then any key to return to menu
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --browser.gatherUsageStats false
echo.
pause
goto menu

:exit
cls
echo Thank you for using TORQ! 🤖
echo.
timeout /t 2 >nul
exit
