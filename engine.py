import os
import time
import queue
import threading
import asyncio
import edge_tts
import pytchat
import re
from playsound3 import playsound

class ChatTTSEngine:
    def __init__(self):
        self.is_running = False
        self.msg_queue = queue.Queue()
        self.audio_queue = queue.Queue()
        self.threads = []
        
        self.msg_dir = "msg_queue"
        self.audio_dir = "temp_audio"
        for d in [self.msg_dir, self.audio_dir]:
            if not os.path.exists(d): os.makedirs(d)

    def extract_video_id(self, url_or_id):
        patterns = [r"v=([a-zA-Z0-9_-]{11})", r"youtu\.be/([a-zA-Z0-9_-]{11})", r"live/([a-zA-Z0-9_-]{11})"]
        for p in patterns:
            m = re.search(p, url_or_id)
            if m: return m.group(1)
        return url_or_id.strip()

    def collector_loop(self, chat):
        print("Collector started")
        processed_ids = set()
        while self.is_running and chat.is_alive():
            try:
                for c in chat.get().sync_items():
                    if c.id not in processed_ids:
                        processed_ids.add(c.id)
                        msg = f"{c.author.name} พูดว่า {c.message}"
                        self.msg_queue.put(msg)
                        if len(processed_ids) > 1000: processed_ids.clear()
            except: pass
            time.sleep(0.5)
        if chat.is_alive(): chat.terminate()

    async def generator_task(self, voice):
        print("Generator started")
        while self.is_running:
            try:
                if not self.msg_queue.empty():
                    text = self.msg_queue.get()
                    path = os.path.join(self.audio_dir, f"{int(time.time()*1000)}.mp3")
                    await edge_tts.Communicate(text, voice).save(path)
                    # ส่ง (Path ไฟล์, จำนวนตัวอักษร) ไปให้ Player
                    self.audio_queue.put((path, len(text)))
                else:
                    await asyncio.sleep(0.1)
            except: pass

    def player_loop(self, delay_per_char, max_delay):
        print(f"Player started (Delay: {delay_per_char}s/char, Max: {max_delay}s)")
        while self.is_running:
            try:
                if not self.audio_queue.empty():
                    path, char_count = self.audio_queue.get()
                    if os.path.exists(path):
                        playsound(path)
                        # คำนวณ Delay หลังเล่นจบ
                        wait_time = min(char_count * delay_per_char, max_delay)
                        if wait_time > 0:
                            time.sleep(wait_time)
                        
                        try: os.remove(path)
                        except: pass
                else:
                    time.sleep(0.1)
            except: pass

    def start(self, video_id, voice, delay_per_char=0.03, max_delay=2.0):
        if self.is_running: return
        vid = self.extract_video_id(video_id)
        try:
            chat = pytchat.create(video_id=vid)
        except Exception as e:
            print(f"Error creating chat: {e}")
            return

        self.is_running = True
        for d in [self.msg_dir, self.audio_dir]:
            if os.path.exists(d):
                for f in os.listdir(d):
                    try: os.remove(os.path.join(d, f))
                    except: pass

        t_col = threading.Thread(target=self.collector_loop, args=(chat,), daemon=True)
        t_gen = threading.Thread(target=lambda: asyncio.run(self.generator_task(voice)), daemon=True)
        t_play = threading.Thread(target=self.player_loop, args=(delay_per_char, max_delay), daemon=True)
        
        self.threads = [t_col, t_gen, t_play]
        for t in self.threads: t.start()

    def stop(self):
        self.is_running = False
        self.threads = []
