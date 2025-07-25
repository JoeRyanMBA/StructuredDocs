@echo off
cd /d "%~dp0backend"
echo [Flask] Starting server...
call .venv\Scripts\activate.bat
set FLASK_APP=app.py
set FLASK_ENV=development
flask run
pause