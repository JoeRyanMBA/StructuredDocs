@echo off
REM Launch both servers and open browser

cd /d "%~dp0"

echo Starting Flask backend...
start "Flask Backend" "%~dp0start_backend.bat"

echo Starting Vite dev server...
start "Vite Dev Server" "%~dp0start_frontend.bat"

REM Wait briefly, then launch browser
timeout /t 3 >nul
start http://localhost:5173

echo Done — Flask and Vite are running in separate windows.
pause