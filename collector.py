import time
import os
import pytchat
from engine import ChatTTSEngine

def main():
    engine = ChatTTSEngine()
    # ในกรณีแยกไฟล์ เราจะใช้ msg_queue folder เป็นสื่อกลางเหมือนเดิมเพื่อให้แยกส่วนได้จริง
    # แต่ใช้ logic ที่สั้นลงจาก ChatTTSEngine
    import configparser
    config = configparser.ConfigParser()
    config.read("config.ini", encoding="utf-8")
    video_id = engine.extract_video_id(config.get("settings", "YOUTUBE_VIDEO_ID", fallback=""))
    
    print(f"Collector Running: {video_id}")
    chat = pytchat.create(video_id=video_id)
    processed_ids = set()

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
        except: pass
        time.sleep(0.5)

if __name__ == "__main__":
    main()
