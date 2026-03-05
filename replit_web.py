import os
import re
import sys
import time
import queue
import threading
import subprocess
from datetime import datetime, timedelta
from collections import deque

from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string
import pytchat

DEFAULT_VOICE = "th-TH-PremwadeeNeural"
TEMP_DIR = "tts_cache_web"
MAX_TTS_CACHE_FILES = 10
PROFANITY_DEFAULT = {"fuck", "shit", "ควย", "สัส", "เหี้ย"}
SPAM_WINDOW_SECONDS = 10
SPAM_REPEAT_THRESHOLD = 3

os.makedirs(TEMP_DIR, exist_ok=True)

app = Flask(__name__)


def extract_video_id(url: str) -> str:
    patterns = [
        r"[?&]v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"youtube\.com/live/([a-zA-Z0-9_-]{11})",
        r"youtube\.com/shorts/([a-zA-Z0-9_-]{11})",
        r"youtube\.com/embed/([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        m = re.search(pattern, url)
        if m:
            return m.group(1)
    return url.strip()


class ReplitTTSState:
    def __init__(self):
        self.running = False
        self.url = ""
        self.voice = DEFAULT_VOICE
        self.logs = deque(maxlen=300)
        self.recent_messages = {}
        self.profanity = set(PROFANITY_DEFAULT)
        self.msg_queue = queue.Queue()
        self.reader_thread = None
        self.tts_thread = None
        self.stop_event = threading.Event()
        self.last_audio = ""
        self.lock = threading.Lock()

    def log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.logs.appendleft(f"[{ts}] {msg}")

    def start(self, url: str, voice: str):
        if self.running:
            self.log("ระบบทำงานอยู่แล้ว")
            return
        self.url = url.strip()
        self.voice = voice.strip() or DEFAULT_VOICE
        if not self.url:
            self.log("กรุณาใส่ URL")
            return

        self.running = True
        self.stop_event.clear()
        self.reader_thread = threading.Thread(target=self.chat_reader_loop, daemon=True)
        self.tts_thread = threading.Thread(target=self.tts_loop, daemon=True)
        self.reader_thread.start()
        self.tts_thread.start()
        self.log(f"เริ่มระบบด้วยเสียง: {self.voice}")

    def stop(self):
        if not self.running:
            return
        self.running = False
        self.stop_event.set()
        self.log("หยุดระบบแล้ว")

    def check_spam(self, author: str, message: str) -> bool:
        key = (author, message)
        now = datetime.now()
        window = timedelta(seconds=SPAM_WINDOW_SECONDS)
        if key not in self.recent_messages:
            self.recent_messages[key] = []
        self.recent_messages[key] = [ts for ts in self.recent_messages[key] if now - ts <= window]
        self.recent_messages[key].append(now)
        return len(self.recent_messages[key]) >= SPAM_REPEAT_THRESHOLD

    def check_profanity(self, message: str) -> bool:
        txt = message.lower()
        return any(bad in txt for bad in self.profanity)

    def cleanup_audio(self):
        files = [os.path.join(TEMP_DIR, f) for f in os.listdir(TEMP_DIR) if f.endswith(".mp3")]
        files.sort(key=os.path.getmtime, reverse=True)
        for old in files[MAX_TTS_CACHE_FILES:]:
            try:
                os.remove(old)
            except OSError:
                pass

    def chat_reader_loop(self):
        try:
            chat = pytchat.create(video_id=extract_video_id(self.url))
            while self.running and chat.is_alive() and not self.stop_event.is_set():
                for c in chat.get().sync_items():
                    author = c.author.name
                    message = c.message
                    if self.check_profanity(message):
                        self.log(f"บล็อกคำต้องห้ามจาก {author}")
                        continue
                    if self.check_spam(author, message):
                        self.log(f"บล็อกสแปมจาก {author}")
                        continue
                    self.msg_queue.put((author, message))
                time.sleep(0.4)
        except Exception as exc:
            self.log(f"ERROR_CHAT: {exc}")
        finally:
            self.running = False

    def tts_loop(self):
        while not self.stop_event.is_set():
            try:
                author, message = self.msg_queue.get(timeout=0.6)
            except queue.Empty:
                continue

            tts_text = f"{author} พูดว่า: {message}"
            filename = os.path.join(TEMP_DIR, f"tts_{int(time.time()*1000)}.mp3")
            cmd = [
                sys.executable,
                "-m",
                "edge_tts",
                "--voice",
                self.voice,
                "--text",
                tts_text,
                "--write-media",
                filename,
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0:
                self.log(f"edge-tts error: {(proc.stderr or proc.stdout).strip()[:120]}")
                continue

            with self.lock:
                self.last_audio = os.path.basename(filename)
            self.log(f"สร้างเสียง: {author} ({len(message)} chars)")
            self.cleanup_audio()


STATE = ReplitTTSState()


HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Chat-TTS Replit</title>
  <meta http-equiv="refresh" content="5">
  <style>
    body { font-family: Arial, sans-serif; background:#111; color:#eee; margin:20px; }
    input { padding:8px; margin:4px; width: 420px; }
    button { padding:8px 12px; margin:4px; }
    .card { background:#1a1a1a; padding:12px; border-radius:10px; margin-bottom:12px; }
    .log { font-family: monospace; white-space: pre-wrap; }
  </style>
</head>
<body>
  <h2>🎧 Chat-TTS (Replit Web)</h2>
  <div class="card">
    <form method="post" action="/start">
      <div><input name="url" placeholder="YouTube live URL" value="{{ url }}"></div>
      <div><input name="voice" placeholder="Voice ID" value="{{ voice }}"></div>
      <button type="submit">Start</button>
      <a href="/stop"><button type="button">Stop</button></a>
    </form>
  </div>

  <div class="card">
    <b>Status:</b> {{ "Running" if running else "Stopped" }}
    {% if last_audio %}
      <div style="margin-top:8px;"><audio controls src="/audio/{{ last_audio }}"></audio></div>
      <div>ล่าสุด: {{ last_audio }}</div>
    {% endif %}
  </div>

  <div class="card">
    <b>Logs (auto refresh 5s)</b>
    <div class="log">{% for line in logs %}{{ line }}\n{% endfor %}</div>
  </div>
</body>
</html>
"""


@app.get("/")
def index():
    with STATE.lock:
        last_audio = STATE.last_audio
    return render_template_string(
        HTML,
        running=STATE.running,
        url=STATE.url,
        voice=STATE.voice,
        logs=list(STATE.logs),
        last_audio=last_audio,
    )


@app.post("/start")
def start():
    STATE.start(request.form.get("url", ""), request.form.get("voice", DEFAULT_VOICE))
    return redirect(url_for("index"))


@app.get("/stop")
def stop():
    STATE.stop()
    return redirect(url_for("index"))


@app.get("/audio/<path:filename>")
def audio(filename):
    return send_from_directory(TEMP_DIR, filename)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
