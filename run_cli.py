import time
import configparser
import sys
from engine import ChatTTSEngine

CONFIG_FILE = "config.ini"

def main():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding="utf-8")
    
    video_id = config.get("settings", "YOUTUBE_VIDEO_ID", fallback="")
    voice = config.get("settings", "VOICE", fallback="th-TH-PremwadeeNeural")
    
    if not video_id:
        video_id = input("Enter YouTube Video ID/URL: ")

    engine = ChatTTSEngine()
    print("--- Chat TTS System Starting (CLI) ---")
    engine.start(video_id, voice)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping system...")
        engine.stop()
        print("System stopped.")

if __name__ == "__main__":
    main()
