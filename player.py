import os
import time
import traceback
from playsound3 import playsound
from logger import get_logger

logger = get_logger("Player")

def main():
    logger.info("Player Running...")
    
    if not os.path.exists("temp_audio"): os.makedirs("temp_audio")

    while True:
        try:
            files = sorted([f for f in os.listdir("temp_audio") if f.endswith(".mp3")])
            for f in files:
                path = os.path.join("temp_audio", f)
                try:
                    logger.debug(f"Playing: {f}")
                    playsound(path)
                    os.remove(path)
                except Exception as e:
                    logger.error(f"Error playing {f}: {e}")
                    # อาจจะย้ายไฟล์ที่มีปัญหาออก หรือลบทิ้งเพื่อไม่ให้ค้าง
                    try: os.remove(path)
                    except: pass
        except Exception as e:
            logger.error(f"Error in player loop: {e}\n{traceback.format_exc()}")
        
        time.sleep(0.5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Player stopped.")
