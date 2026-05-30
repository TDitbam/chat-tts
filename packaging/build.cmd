@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo   Chat TTS Auto-Build Script
echo ==========================================

:: 1. Install Requirements
echo [1/4] Checking and installing dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b %errorlevel%
)

:: 2. Build EXE
echo.
echo [2/4] Building Executable (ChatTTS.exe)...
echo This may take a few minutes...
python -m PyInstaller --onefile --name ChatTTS --clean --collect-all customtkinter --noconsole ..\start_gui.py
if %errorlevel% neq 0 (
    echo [ERROR] Build failed.
    pause
    exit /b %errorlevel%
)

:: 3. Package to ZIP
echo.
echo [3/4] Packaging into ZIP...
powershell -Command "Compress-Archive -Path 'dist\ChatTTS.exe', '..\README.md', '..\LICENSE', '..\docs\manual_th.md' -DestinationPath '..\ChatTTS-v2.2.1-Windows.zip' -Force"
if %errorlevel% neq 0 (
    echo [ERROR] Packaging failed.
    pause
    exit /b %errorlevel%
)

:: 4. Cleanup
echo.
echo [4/4] Cleaning up temporary files...
if exist build rmdir /s /q build
if exist ChatTTS.spec del /f /q ChatTTS.spec

echo.
echo ==========================================
echo   BUILD SUCCESSFUL!
echo   Output: ChatTTS-v2.2.1-Windows.zip
echo ==========================================
pause
