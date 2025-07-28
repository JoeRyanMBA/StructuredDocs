@echo off
cd /d "%~dp0backend"
echo [Flask] Starting server...
call .venv\Scripts\activate.bat
echo [Flask] Virtual environment activated
echo [Flask] Working directory: %CD%
set FLASK_APP=app.py
set FLASK_ENV=development
echo [Flask] Environment variables set
echo [Flask] Attempting to start with flask command...
flask run --host=0.0.0.0 --port=5000 --debug
if %ERRORLEVEL% NEQ 0 (
    echo [Flask] Flask command failed, trying python -m flask...
    python -m flask --app app.py run --host=0.0.0.0 --port=5000 --debug
)
if %ERRORLEVEL% NEQ 0 (
    echo [Flask] Flask module failed, trying direct python execution...
    python app.py
)
pause