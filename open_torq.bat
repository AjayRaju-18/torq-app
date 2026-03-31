@echo off
echo Opening TORQ Web App...
echo.
echo Starting TORQ - Mechanical Engineering Assistant
echo Please wait while the app loads in your browser...
echo.

REM Open the Streamlit Community Cloud URL in default browser
start "" "https://torq-app-dbd36yhetgbc7epzhitxhd.streamlit.app/"

REM Alternative: If you want to run locally instead, uncomment the lines below and comment the line above
REM echo Starting local Streamlit server...
REM cd /d "%~dp0"
REM streamlit run app.py --server.port 8501 --server.address 0.0.0.0

echo TORQ app should now be opening in your browser!
echo.
pause