@echo off
echo Cleaning up caches and build artifacts...

REM — Remove Vite cache
if exist frontend\node_modules\.vite (
  rd /s /q frontend\node_modules\.vite
  echo Removed frontend\node_modules\.vite
)

REM — Remove Vite build output
if exist frontend\dist (
  rd /s /q frontend\dist
  echo Removed frontend\dist
)

REM — Remove root Vite cache (if present)
if exist .vite (
  rd /s /q .vite
  echo Removed .vite
)

REM — Remove Python byte-cache folders
for /d %%F in (backend\**\__pycache__) do (
  rd /s /q "%%F"
  echo Removed %%F
)

echo Cleanup complete.
pause