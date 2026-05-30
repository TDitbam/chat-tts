@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo   Chat TTS Auto-Build Script
echo ==========================================

:: 1. Install Requirements
echo [1/5] Checking and installing dependencies...
python -m pip install -r ..\requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b %errorlevel%
)

:: 2. Build EXEs
echo.
echo [2/5] Building Executables...
echo Building GUI...
python -m PyInstaller --onefile --name ChatTTS --clean --collect-all customtkinter --noconsole ..\start_gui.py
echo Building CLI...
python -m PyInstaller --onefile --name ChatTTS-CLI --clean ..\start_cli.py

if %errorlevel% neq 0 (
    echo [ERROR] Build failed.
    pause
    exit /b %errorlevel%
)

:: 3. Package to ZIP
echo.
echo [3/5] Packaging into ZIP...
powershell -Command "Compress-Archive -Path 'dist\ChatTTS.exe', 'dist\ChatTTS-CLI.exe', '..\README.md', '..\LICENSE', '..\docs\manual_th.md' -DestinationPath '..\ChatTTS-v2.2.1-Windows.zip' -Force"
if %errorlevel% neq 0 (
    echo [ERROR] Packaging failed.
    pause
    exit /b %errorlevel%
)

:: 4. Build Installer (Inno Setup)
echo.
echo [4/5] Building Installer (Inno Setup)...
set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "!ISCC!" (
    "!ISCC!" setup.iss
) else (
    echo [SKIP] Inno Setup compiler (ISCC.exe) not found in default path.
    echo Please compile 'packaging\setup.iss' manually.
)

:: 5. Cleanup
echo.
echo [5/5] Cleaning up temporary files...
if exist build rmdir /s /q build
if exist ChatTTS.spec del /f /q ChatTTS.spec
if exist ChatTTS-CLI.spec del /f /q ChatTTS-CLI.spec

echo.
echo ==========================================
echo   BUILD SUCCESSFUL!
echo   Output: ChatTTS-v2.2.1-Windows.zip
echo   Output: ChatTTS-v2.2.1-Setup.exe (if ISCC available)
echo ==========================================
pause

