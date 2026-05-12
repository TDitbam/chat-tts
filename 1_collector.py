import os
import time
import configparser
import re
import pytchat

CONFIG_FILE = "config.ini"
MSG_DIR = "msg_queue"

if not os.path.exists(MSG_DIR):
    os.makedirs(MSG_DIR)

def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding="utf-8")
    return config

def extract_video_id(url_or_id):
    patterns = [r"v=([a-zA-Z0-9_-]{11})", r"youtu\.be/([a-zA-Z0-9_-]{11})", r"live/([a-zA-Z0-9_-]{11})"]
    for p in patterns:
        m = re.search(p, url_or_id)
        if m: return m.group(1)
    return url_or_id.strip()

def main():
    config = load_config()
    video_id = extract_video_id(config.get("settings", "YOUTUBE_VIDEO_ID", fallback=""))
    
    print(f"Chat Collector Running (ID: {video_id})...")
    chat = pytchat.create(video_id=video_id)

    while chat.is_alive():
        for c in chat.get().sync_items():
            msg = f"{c.author.name} พูดว่า {c.message}"
            # สร้างไฟล์ข้อความตาม Timestamp
            filename = os.path.join(MSG_DIR, f"{int(time.time()*1000)}.txt")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(msg)
            print(f"New Msg: {msg}")
        time.sleep(0.5)

if __name__ == "__main__":
    main()