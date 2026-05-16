import os
import time
import queue
import threading
import asyncio
import edge_tts
import re
import traceback
from deep_translator import GoogleTranslator
from playsound3 import playsound
from logger import get_logger
from gtts import gTTS

# Import platform collectors
from youtube_collector import youtube_collector
from facebook_collector import facebook_collector
from twitch_collector import twitch_collector
from tiktok_collector import tiktok_collector

logger = get_logger("Engine")

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
        
        self.voice = "th-TH-PremwadeeNeural"
        self.delay_per_char = 0.03
        self.max_delay = 2.0
        self.auto_translate = False
        self.translator = GoogleTranslator(source='auto', target='th')

    def extract_video_id(self, url_or_id):
        patterns = [
            r"v=([a-zA-Z0-9_-]{11})", 
            r"youtu\.be/([a-zA-Z0-9_-]{11})", 
            r"live/([a-zA-Z0-9_-]{11})",
            r"video/([a-zA-Z0-9_-]{11})/livestreaming"
        ]
        for p in patterns:
            m = re.search(p, url_or_id)
            if m: return m.group(1)
        return url_or_id.strip()

    async def generator_task(self):
        logger.info(f"Generator started: {self.voice}")
        while self.is_running:
            try:
                if not self.msg_queue.empty():
                    data = self.msg_queue.get()
                    if isinstance(data, str):
                        text = data
                    else:
                        author = data.get("author", "Unknown")
                        message = data.get("message", "")
                        
                        if self.auto_translate:
                            try:
                                if not any('\u0e00' <= char <= '\u0e7f' for char in message):
                                    translated = self.translator.translate(message)
                                    logger.info(f"Translated: {message} -> {translated}")
                                    message = translated
                            except Exception as te:
                                logger.error(f"Translation Error: {te}")
                        
                        text = f"{author} พูดว่า {message}"

                    path = os.path.join(self.audio_dir, f"{int(time.time()*1000)}.mp3")
                    
                    try:
                        # Primary: edge-tts
                        await edge_tts.Communicate(text, self.voice).save(path)
                    except Exception as e:
                        logger.warning(f"edge-tts failed, using gTTS fallback: {e}")
                        # Fallback: gTTS
                        try:
                            # Extract language code (e.g., th-TH -> th)
                            lang_code = self.voice.split('-')[0] if '-' in self.voice else 'th'
                            tts = gTTS(text=text, lang=lang_code)
                            # gTTS save is blocking, but it's okay in this thread
                            tts.save(path)
                        except Exception as ge:
                            logger.error(f"gTTS fallback also failed: {ge}")
                            continue
                    
                    self.audio_queue.put((path, len(text)))
                else:
                    await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Generator Error: {e}")
                await asyncio.sleep(1)

    def player_loop(self):
        logger.info("Player started")
        while self.is_running:
            try:
                if not self.audio_queue.empty():
                    path, char_count = self.audio_queue.get()
                    if os.path.exists(path):
                        try:
                            playsound(path)
                            time.sleep(min(char_count * self.delay_per_char, self.max_delay))
                        except Exception as e: logger.error(f"Play Error: {e}")
                        finally:
                            try: os.remove(path)
                            except: pass
                else: time.sleep(0.1)
            except Exception as e: logger.error(f"Player Loop Error: {e}")

    def start(self, config_dict):
        if self.is_running: return
        self.is_running = True
        
        self.voice = config_dict.get("voice", "th-TH-PremwadeeNeural")
        self.delay_per_char = float(config_dict.get("delay_per_char", 0.03))
        self.max_delay = float(config_dict.get("max_delay", 2.0))
        self.auto_translate = config_dict.get("auto_translate") == "True"
        
        def run_engine():
            try:
                # Cleanup in background thread
                logger.info("Cleaning up old files...")
                for d in [self.msg_dir, self.audio_dir]:
                    if os.path.exists(d):
                        for f in os.listdir(d):
                            try: os.remove(os.path.join(d, f))
                            except: pass
                
                # Core Threads
                self.threads = [
                    threading.Thread(target=lambda: asyncio.run(self.generator_task()), daemon=True),
                    threading.Thread(target=self.player_loop, daemon=True)
                ]

                # Conditional Collectors
                if config_dict.get("yt_enabled") == "True" and config_dict.get("yt_id"):
                    vid = self.extract_video_id(config_dict.get("yt_id", ""))
                    self.threads.append(threading.Thread(target=youtube_collector, args=(vid, self.msg_queue, lambda: self.is_running), daemon=True))
                
                if config_dict.get("fb_enabled") == "True" and config_dict.get("fb_url"):
                    url = config_dict.get("fb_url", "")
                    self.threads.append(threading.Thread(target=facebook_collector, args=(url, self.msg_queue, lambda: self.is_running), daemon=True))
                    
                if config_dict.get("tw_enabled") == "True" and config_dict.get("tw_channel"):
                    channel = config_dict.get("tw_channel", "")
                    self.threads.append(threading.Thread(target=twitch_collector, args=(channel, self.msg_queue, lambda: self.is_running), daemon=True))

                if config_dict.get("tk_enabled") == "True" and config_dict.get("tk_username"):
                    username = config_dict.get("tk_username", "")
                    self.threads.append(threading.Thread(target=tiktok_collector, args=(username, self.msg_queue, lambda: self.is_running), daemon=True))

                for t in self.threads: t.start()
                logger.info(f"Engine started with {len(self.threads)-2} collectors")
            except Exception as e:
                logger.error(f"Failed to start engine: {e}\n{traceback.format_exc()}")
                self.is_running = False

        # Execute everything in a separate thread to keep GUI responsive
        threading.Thread(target=run_engine, daemon=True).start()

    def stop(self):
        self.is_running = False
        self.threads = []
        logger.info("Engine stopped")
