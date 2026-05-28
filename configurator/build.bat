@echo off
REM Build script for ModScreenManager Configurator
REM This script builds the application using PyInstaller

echo ========================================
echo Building ModScreenManager Configurator
echo ========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Navigate to configurator directory (script is inside configurator folder)
cd /d "%~dp0"

REM Check if pyinstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Run the build
echo.
echo Starting build...
python build.py

if errorlevel 1 (
    echo.
    echo Build FAILED
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo Output: configurator\dist\configurator
echo ========================================
pause