@echo off
REM ============================================================
REM AI Study Companion - Java Launcher Batch Script
REM ============================================================
REM This script compiles and runs the Java launcher which
REM will start the Python application in the background
REM ============================================================

echo.
echo ========================================
echo  AI Study Companion - Java Launcher
echo ========================================
echo.

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check if Java is installed
echo [1/3] Checking Java installation...
java -version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Java is not installed or not in PATH
    echo.
    echo Please install Java JDK 8 or higher from:
    echo https://www.oracle.com/java/technologies/downloads/
    echo.
    pause
    exit /b 1
)
echo [OK] Java found
echo.

REM Check if Python is installed
echo [2/3] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [WARNING] Python is not installed or not in PATH
    echo The Java launcher will attempt to run but may fail
    echo.
    echo Please install Python 3.8-3.12 from:
    echo https://www.python.org/downloads/
    echo.
    pause
)
echo [OK] Python found
echo.

REM Compile the Java launcher if needed
echo [3/3] Compiling Java launcher...
if not exist "StudyCompanionLauncher.class" (
    echo Compiling StudyCompanionLauncher.java...
    javac StudyCompanionLauncher.java
    if errorlevel 1 (
        echo.
        echo [ERROR] Compilation failed
        echo.
        pause
        exit /b 1
    )
    echo [OK] Compilation successful
) else (
    REM Check if source is newer than class file
    for %%A in (StudyCompanionLauncher.java) do set "SOURCE_TIME=%%~tA"
    for %%A in (StudyCompanionLauncher.class) do set "CLASS_TIME=%%~tA"
    
    REM Always recompile if java file exists (simple approach)
    if exist "StudyCompanionLauncher.java" (
        echo Recompiling StudyCompanionLauncher.java...
        javac StudyCompanionLauncher.java
        if errorlevel 1 (
            echo.
            echo [ERROR] Compilation failed
            echo.
            pause
            exit /b 1
        )
        echo [OK] Compilation successful
    )
)
echo.

REM Run the Java launcher
echo ========================================
echo  Starting AI Study Companion...
echo ========================================
echo.
echo Press Ctrl+C to stop the application
echo.

REM Remove trailing backslash from path if present
set "PROJECT_PATH=%SCRIPT_DIR%"
if "%PROJECT_PATH:~-1%"=="\" set "PROJECT_PATH=%PROJECT_PATH:~0,-1%"

java StudyCompanionLauncher --path "%PROJECT_PATH%"

REM Check exit code
if errorlevel 1 (
    echo.
    echo [ERROR] Application exited with an error
    echo.
    pause
    exit /b 1
)

echo.
echo Application closed successfully
pause
