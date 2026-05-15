import os
import time
import asyncio
import edge_tts
import configparser
import traceback
from logger import get_logger

logger = get_logger("Generator")

async def main():
    logger.info("Generator Running...")
    config = configparser.ConfigParser()
    
    if not os.path.exists("msg_queue"): os.makedirs("msg_queue")
    if not os.path.exists("temp_audio"): os.makedirs("temp_audio")

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
                    logger.debug(f"Generating audio for: {text[:20]}...")
                    await edge_tts.Communicate(text, voice).save(audio_path)
                    os.remove(txt_path)
                except Exception as e:
                    logger.error(f"Error generating audio for {f}: {e}")
        except Exception as e:
            logger.error(f"Error in generator loop: {e}\n{traceback.format_exc()}")
        
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Generator stopped.")
