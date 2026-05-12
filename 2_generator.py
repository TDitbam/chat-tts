import os
import time
import asyncio
import edge_tts
import configparser

MSG_DIR = "msg_queue"
AUDIO_DIR = "temp_audio"
CONFIG_FILE = "config.ini"

for d in [MSG_DIR, AUDIO_DIR]:
    if not os.path.exists(d): os.makedirs(d)

def load_voice_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding="utf-8")
    return config.get("settings", "VOICE", fallback="th-TH-PremwadeeNeural")

async def generate_tts(text, filename, voice):
    file_path = os.path.join(AUDIO_DIR, f"{filename}.mp3")
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(file_path)

def main():
    print("TTS Generator Running...")
    while True:
        voice = load_voice_config()
        files = sorted([f for f in os.listdir(MSG_DIR) if f.endswith(".txt")])
        if files:
            for f in files:
                txt_path = os.path.join(MSG_DIR, f)
                try:
                    with open(txt_path, "r", encoding="utf-8") as file:
                        text = file.read()
                    
                    print(f"Generating TTS with voice {voice}: {text[:20]}...")
                    asyncio.run(generate_tts(text, f.replace(".txt", ""), voice))
                    
                    os.remove(txt_path) 
                except Exception as e:
                    print(f"Gen Error: {e}")
        time.sleep(0.1)

if __name__ == "__main__":
    main()