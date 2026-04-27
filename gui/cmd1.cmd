@echo off
chcp 65001 >nul
echo [*] Building chat-tts.exe ...

py -m PyInstaller ^
  --onefile ^
  --clean ^
  --name chat-tts ^
  --add-data "config.ini;." ^
  --add-data "api.py;." ^
  --icon=icon.ico ^
  --hidden-import=edge_tts ^
  --hidden-import=playsound3 ^
  main.py

echo.
if exist "dist\chat-tts.exe" (
    echo [OK] Build สำเร็จ: dist\chat-tts.exe
) else (
    echo [ERR] Build ล้มเหลว
)
pause