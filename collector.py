import time
import os
import pytchat
import configparser
import traceback
from engine import ChatTTSEngine
from logger import get_logger

logger = get_logger("Collector")

def main():
    engine = ChatTTSEngine()
    config = configparser.ConfigParser()
    config.read("config.ini", encoding="utf-8")
    
    video_id_raw = config.get("settings", "YOUTUBE_VIDEO_ID", fallback="")
    video_id = engine.extract_video_id(video_id_raw)
    
    if not video_id:
        logger.error("No YouTube Video ID found in config.ini")
        return

    logger.info(f"Collector Running: {video_id}")
    processed_ids = set()

    while True:
        try:
            chat = pytchat.create(video_id=video_id, interruptable=False)
            if not chat.is_alive():
                logger.error("Failed to connect to chat. Retrying in 5 seconds...")
                time.sleep(5)
                continue

            logger.info("Chat connected.")
            while chat.is_alive():
                try:
                    for c in chat.get().sync_items():
                        if c.id not in processed_ids:
                            processed_ids.add(c.id)
                            msg = f"{c.author.name} พูดว่า {c.message}"
                            path = os.path.join("msg_queue", f"{int(time.time()*1000)}.txt")
                            with open(path, "w", encoding="utf-8") as f:
                                f.write(msg)
                            if len(processed_ids) > 1000: processed_ids.clear()
                except Exception as e:
                    logger.warning(f"Error getting items: {e}")
                    break
                time.sleep(0.5)
            
            logger.warning("Chat connection lost. Reconnecting...")
            time.sleep(2)
        except Exception as e:
            logger.error(f"Unexpected error: {e}\n{traceback.format_exc()}")
            time.sleep(5)

if __name__ == "__main__":
    main()
