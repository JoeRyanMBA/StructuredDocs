@echo off
echo Resetting development environments…

REM — Recreate Python virtualenv and reinstall
if exist backend\.venv (
  rd /s /q backend\.venv
  echo Removed old backend\.venv
)
python -m venv backend\.venv
echo Created new backend\.venv

call backend\.venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r backend\requirements.txt
deactivate
echo Python dependencies installed.

REM — Reinstall frontend packages
cd frontend
if exist node_modules (
  rd /s /q node_modules
  echo Removed old frontend\node_modules
)
npm ci
cd ..
echo Frontend dependencies installed.

echo Reset complete.
pause