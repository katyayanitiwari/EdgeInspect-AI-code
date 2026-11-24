@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run setup_windows.bat first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" inference\detect.py --weights experiments\EXP-002\weights\best.pt --source 0 --imgsz 320
pause
