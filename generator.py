import os
import time
import asyncio
import edge_tts
import configparser

async def main():
    print("Generator Running...")
    config = configparser.ConfigParser()
    
    while True:
        try:
            config.read("config.ini", encoding="utf-8")
            voice = config.get("settings", "VOICE", fallback="th-TH-PremwadeeNeural")
            files = sorted([f for f in os.listdir("msg_queue") if f.endswith(".txt")])
            
            for f in files:
                txt_path = os.path.join("msg_queue", f)
                try:
                    with open(txt_path, "r", encoding="utf-8") as file:
                        text = file.read()
                    
                    audio_path = os.path.join("temp_audio", f.replace(".txt", ".mp3"))
                    await edge_tts.Communicate(text, voice).save(audio_path)
                    os.remove(txt_path)
                except: pass
        except: pass
        await asyncio.sleep(0.2)

if __name__ == "__main__":
    asyncio.run(main())
