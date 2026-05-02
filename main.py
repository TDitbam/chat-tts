import os
import sys
import time
import queue
import threading
import asyncio
import configparser
import re

import pytchat
import edge_tts
from playsound3 import playsound

sys.stdout.reconfigure(encoding="utf-8")

# ================= CONFIG =================
CONFIG_FILE = "config.ini"

def load_config():
    config = configparser.ConfigParser()
    if not config.read(CONFIG_FILE, encoding="utf-8"):
        print("❌ ไม่พบ config.ini")
        sys.exit(1)
    return config

def extract_video_id(url_or_id: str) -> str:
    if "http" not in url_or_id:
        return url_or_id.strip()

    patterns = [
        r"v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"live/([a-zA-Z0-9_-]{11})"
    ]

    for p in patterns:
        m = re.search(p, url_or_id)
        if m:
            return m.group(1)

    return url_or_id

config = load_config()

YOUTUBE_VIDEO_ID = extract_video_id(
    config.get("settings", "YOUTUBE_VIDEO_ID", fallback="")
)

PRIMARY_VOICE = "th-TH-PremwadeeNeural"
FALLBACK_VOICES = ["th-TH-AcharaNeural", "en-US-JennyNeural"]

DELAY_PER_CHAR = config.getfloat("settings", "DELAY_PER_CHAR", fallback=0.03)
MAX_DELAY = config.getfloat("settings", "MAX_DELAY", fallback=2.0)

audio_queue = queue.Queue(maxsize=50)

# ================= UTILS =================
def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def calc_delay(text):
    return min(len(text) * DELAY_PER_CHAR, MAX_DELAY)

def safe_filename():
    return f"tts_{int(time.time()*1000)}.mp3"

# ================= TTS =================
async def tts_try(text, file_path):
    for voice in [PRIMARY_VOICE] + FALLBACK_VOICES:
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(file_path)
            return True
        except Exception:
            log(f"voice fail: {voice}")
    return False

def tts_worker():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        try:
            text = audio_queue.get(timeout=1)
        except queue.Empty:
            continue

        file_path = safe_filename()

        try:
            log(f"TTS: {text[:40]}")

            ok = loop.run_until_complete(tts_try(text, file_path))

            if ok and os.path.exists(file_path):
                log(f"▶️ PLAY {file_path}")
                playsound(file_path)
            else:
                log("❌ generate fail")

        except Exception as e:
            log(f"TTS ERROR: {e}")

        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

        time.sleep(calc_delay(text))

# ================= MAIN =================
def main():
    log("=== START ===")

    threading.Thread(target=tts_worker, daemon=True).start()

    while True:
        try:
            log("Connecting chat...")
            chat = pytchat.create(video_id=YOUTUBE_VIDEO_ID)

            while chat.is_alive():
                for c in chat.get().sync_items():
                    msg = f"{c.author.name} พูดว่า {c.message}"
                    log(msg)

                    try:
                        audio_queue.put_nowait(msg)
                    except queue.Full:
                        log("⚠️ queue full")

                time.sleep(0.5)

        except Exception as e:
            log(f"CHAT ERROR: {e}")

        log("♻️ reconnect 5s")
        time.sleep(5)

if __name__ == "__main__":
    main()