import time
import pytchat
from logger import get_logger

logger = get_logger("YouTube")

def youtube_collector(video_id, msg_queue, is_running_func):
    logger.info(f"YouTube Collector started: {video_id}")
    processed_ids = set()
    while is_running_func():
        try:
            chat = pytchat.create(video_id=video_id, interruptable=False)
            while is_running_func() and chat.is_alive():
                for c in chat.get().sync_items():
                    if c.id not in processed_ids:
                        processed_ids.add(c.id)
                        msg_queue.put({"author": c.author.name, "message": c.message})
                        if len(processed_ids) > 1000: processed_ids.clear()
                time.sleep(0.5)
            if is_running_func(): time.sleep(5)
        except Exception as e:
            logger.error(f"YouTube Error: {e}")
            time.sleep(5)
