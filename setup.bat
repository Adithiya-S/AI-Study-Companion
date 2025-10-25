@echo off
REM ============================================================
REM AI Study Companion - Quick Setup Script
REM ============================================================
REM This script installs all dependencies and sets up the app
REM ============================================================

echo.
echo ========================================
echo  AI Study Companion - Quick Setup
echo ========================================
echo.

REM Check Python 3.11
echo [1/3] Checking Python 3.11 installation...

REM Try to find Python 3.11
set "PYTHON_CMD="

REM Try py launcher with 3.11
py -3.11 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py -3.11"
    goto :python_found
)

REM Try python3.11 directly
python3.11 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python3.11"
    goto :python_found
)

REM Try python311
python311 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python311"
    goto :python_found
)

REM Fall back to default python (with warning)
python --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python"
    echo [WARNING] Python 3.11 not found, using default Python
    python --version
    echo [RECOMMENDATION] Install Python 3.11 for best compatibility
    echo.
    goto :python_found
)

REM No Python found
echo.
echo [ERROR] Python is not installed or not in PATH
echo Please install Python 3.11 from: https://www.python.org/downloads/release/python-3110/
echo.
pause
exit /b 1

:python_found
%PYTHON_CMD% --version
echo.

REM Install dependencies
echo [2/3] Installing dependencies...
echo This may take a few minutes...
echo.

%PYTHON_CMD% -m pip install --upgrade pip
if errorlevel 1 (
    echo [WARNING] Could not upgrade pip, continuing...
)

%PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] All dependencies installed successfully!
echo.

REM Run integrity check
echo [3/3] Running integrity check...
echo.

%PYTHON_CMD% check_integrity.py

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo To run the app:
echo   1. Double-click main.py, or
echo   2. Run: %PYTHON_CMD% main.py, or
echo   3. Use Java launcher: run_launcher.bat
echo.
pause
