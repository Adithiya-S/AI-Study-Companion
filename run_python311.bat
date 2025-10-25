@echo off
REM ============================================================
REM AI Study Companion - Run with Python 3.11
REM ============================================================
REM This script specifically runs the app with Python 3.11
REM ============================================================

echo.
echo ========================================
echo  AI Study Companion (Python 3.11)
echo ========================================
echo.

REM Set the directory to where the script is located
cd /d "%~dp0"

REM Try to find Python 3.11
set "PYTHON_CMD="

REM Try py launcher with 3.11 (Windows Python Launcher)
py -3.11 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py -3.11"
    echo ✅ Found Python 3.11 via py launcher
    goto :run_app
)

REM Try python3.11 directly
python3.11 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python3.11"
    echo ✅ Found Python 3.11
    goto :run_app
)

REM Try python311
python311 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python311"
    echo ✅ Found Python 3.11
    goto :run_app
)

REM Try specific paths
if exist "C:\Python311\python.exe" (
    set "PYTHON_CMD=C:\Python311\python.exe"
    echo ✅ Found Python 3.11 at C:\Python311\
    goto :run_app
)

if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    echo ✅ Found Python 3.11 in user directory
    goto :run_app
)

REM Python 3.11 not found
echo.
echo ❌ ERROR: Python 3.11 not found!
echo.
echo Python 3.11 is REQUIRED for this application to work properly.
echo Python 3.13+ has compatibility issues with MediaPipe (camera features).
echo.
echo Please install Python 3.11 from:
echo https://www.python.org/downloads/release/python-3110/
echo.
echo Installation tips:
echo   1. Download "Windows installer (64-bit)"
echo   2. Check "Add Python 3.11 to PATH" during installation
echo   3. Restart this script after installation
echo.
pause
exit /b 1

:run_app
echo.
echo Python Version:
%PYTHON_CMD% --version
echo.
echo Starting AI Study Companion...
echo.

REM Run the application
%PYTHON_CMD% main.py

REM Check if there was an error
if errorlevel 1 (
    echo.
    echo ❌ Application exited with an error
    echo.
    pause
    exit /b 1
)

echo.
echo Application closed successfully
pause
