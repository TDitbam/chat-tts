import os
import sys
import time
import queue
import threading
import asyncio
import configparser
import re
from tkinter import *
import pytchat
import edge_tts
from playsound3 import playsound


# ================= SAFE STDOUT =================
try:
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except:
    pass

# ================= CONFIG =================
CONFIG_FILE = "config.ini"

def load_config():
    config = configparser.ConfigParser()
    if not config.read(CONFIG_FILE, encoding="utf-8"):
        print("❌ ไม่พบ config.ini")
        sys.exit(1)
    return config

def extract_video_id(url_or_id: str) -> str:
    if not url_or_id:
        return ""

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

    return url_or_id.strip()

config = load_config()

YOUTUBE_VIDEO_ID = extract_video_id(
    config.get("settings", "YOUTUBE_VIDEO_ID", fallback="")
)

PRIMARY_VOICE = "th-TH-PremwadeeNeural"
FALLBACK_VOICES = [
    "th-TH-th-TH-AcharaNeural",
    "th-TH-NiwatNeural"
]

DELAY_PER_CHAR = config.getfloat("settings", "DELAY_PER_CHAR", fallback=0.03)
MAX_DELAY      = config.getfloat("settings", "MAX_DELAY", fallback=2.0)

# ================= GLOBAL =================
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
    voices = [PRIMARY_VOICE] + FALLBACK_VOICES

    for voice in voices:
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(file_path)
            return True
        except Exception as e:
            log(f"voice fail: {voice} | {e}")

    return False

def tts_worker():
    while True:
        try:
            text = audio_queue.get(timeout=1)
        except queue.Empty:
            continue

        file_path = safe_filename()

        try:
            log(f"TTS: {text[:40]}")

            # 🔥 FIX หลัก: ไม่ใช้ loop เดิมแล้ว
            ok = asyncio.run(tts_try(text, file_path))

            if ok and os.path.exists(file_path):
                log(f"▶️ PLAY {file_path}")
                playsound(file_path)
            else:
                log("❌ generate fail")

        except Exception as e:
            log(f"TTS ERROR: {e}")

        finally:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass

        time.sleep(calc_delay(text))


def obs():
    root = Tk()
    root.title("OBS Version")

    Label(text="OBS Sound Version Stating").pack()

    root.mainloop()

# ================= MAIN =================
def main():

    log("=== START SYSTEM ===")

    threading.Thread(target=tts_worker, daemon=True).start()

    threading.Thread(target=obs, daemon=True).start()

    while True:
        chat = None
        last_msg_time = time.time()

        try:
            if not YOUTUBE_VIDEO_ID:
                log("❌ ไม่มี YOUTUBE_VIDEO_ID")
                time.sleep(5)
                continue

            log("Connecting chat...")
            chat = pytchat.create(video_id=YOUTUBE_VIDEO_ID)

            while chat.is_alive():
                data = chat.get()
                items = list(data.sync_items())

                if items:
                    last_msg_time = time.time()

                for c in items:
                    msg = f"{c.author.name} พูดว่า {c.message}".strip()

                    try:
                        audio_queue.put_nowait(msg)
                    except queue.Full:
                        log("⚠️ queue full")

                # timeout กันค้าง
                if time.time() - last_msg_time > 60:
                    log("⚠️ timeout reconnect")
                    break

                time.sleep(0.5)

        except Exception as e:
            log(f"CHAT ERROR: {e}")

        finally:
            if chat is not None:
                try:
                    chat.terminate()
                except:
                    pass

        log("♻️ restart 5s")
        time.sleep(5)

# ================= RUN =================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("🛑 stopped")