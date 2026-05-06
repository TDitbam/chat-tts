py -m PyInstaller --onefile --clean --name chat-tts --icon icon.ico --add-data "config.ini;." main.py
py -m PyInstaller --onefile --noconsole --name chat-tts-config config_gui.py