@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo EdgeInspect-AI - Windows environment setup
echo ============================================================

py -3.11 --version >nul 2>&1
if errorlevel 1 (
  echo ERROR: Python 3.11 x64 was not found through the Python Launcher.
  echo Install Python 3.11 x64, enable the Python Launcher, then run this file again.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating project virtual environment...
  py -3.11 -m venv .venv
  if errorlevel 1 goto :failed
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 goto :failed

python -m pip install --upgrade pip
if errorlevel 1 goto :failed

echo Installing PyTorch CPU build for a consistent first baseline...
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 goto :failed

echo Installing project dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 goto :failed

echo Running environment checks...
python check_windows_env.py
if errorlevel 1 goto :failed

echo.
echo SETUP COMPLETE. Use run_webcam_windows.bat or run_dashboard_windows.bat.
pause
exit /b 0

:failed
echo.
echo SETUP FAILED. Copy the complete error output and send it here.
pause
exit /b 1
