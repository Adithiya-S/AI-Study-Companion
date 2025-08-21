@echo off
echo ========================================
echo Study Focus App - Python 3.8-3.12 Compatible
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8-3.12 from python.org
    pause
    exit /b 1
)

REM Check Python version compatibility
python -c "import sys; exit(0 if (3,8) <= sys.version_info <= (3,12) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Incompatible Python version detected
    echo This app requires Python 3.8-3.12
    echo Python 3.13+ is not yet supported due to MediaPipe limitations
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    echo Try running as administrator
    pause
    exit /b 1
)

REM Launch the application
echo.
echo Starting Study Focus App...
echo.
python main.py

REM Keep window open if there's an error
if %errorlevel% neq 0 (
    echo.
    echo Application exited with error
    pause
)
