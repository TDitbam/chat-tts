import os
import time
import queue
import threading
import asyncio
import re
import traceback
from typing import Dict, Any, Optional

import edge_tts
from deep_translator import GoogleTranslator
from pygame import mixer
from gtts import gTTS

from .app_logger import get_logger, get_app_dir
from .collectors.yt_chat import youtube_collector
from .collectors.twitch_chat import twitch_collector
from .collectors.tiktok_chat import tiktok_collector

logger = get_logger("Engine")

class ChatTTSEngine:
    def __init__(self):
        self.is_running = False
        self.current_session_id = 0
        self.msg_queue = queue.Queue(maxsize=100)
        self.audio_queue = queue.Queue(maxsize=100)
        self.seen_messages = set()
        self.max_seen_messages = 500
        self.threads = []
        
        # ใช้ AppData แทนโฟลเดอร์ปัจจุบัน
        app_dir = get_app_dir()
        self.msg_dir = os.path.join(app_dir, "msg_queue")
        self.audio_dir = os.path.join(app_dir, "temp_audio")
        self.profanity_file = os.path.join(app_dir, "bad_words.txt")
        
        self._ensure_directories()
        
        self.voice = "th-TH-PremwadeeNeural"
        self.delay_per_char = 0.03
        self.max_delay = 2.0
        self.auto_translate = False
        self.translator = GoogleTranslator(source='auto', target='th')
        
        # Profanity Filter
        self.profanity_enabled = False
        self.profanity_list = []
        self._load_profanity_list()
        
        self._init_mixer()

    def _clear_queues(self):
        """Empty both message and audio queues."""
        while not self.msg_queue.empty():
            try: self.msg_queue.get_nowait()
            except queue.Empty: break
            
        while not self.audio_queue.empty():
            try: self.audio_queue.get_nowait()
            except queue.Empty: break
        logger.info("Queues cleared.")

    def _load_profanity_list(self):
        """Load profanity list from file."""
        if os.path.exists(self.profanity_file):
            try:
                with open(self.profanity_file, "r", encoding="utf-8") as f:
                    self.profanity_list = [line.strip().lower() for line in f if line.strip()]
                logger.info(f"Loaded {len(self.profanity_list)} profanity words.")
            except Exception as e:
                logger.error(f"Failed to load profanity list: {e}")
        else:
            self.profanity_list = []

    def _ensure_directories(self):
        """Create necessary directories if they don't exist."""
        for d in [self.msg_dir, self.audio_dir]:
            if not os.path.exists(d): 
                os.makedirs(d)

    def _init_mixer(self):
        """Initialize pygame mixer."""
        try:
            mixer.init()
        except Exception as e:
            logger.error(f"Failed to initialize pygame mixer: {e}")

    def _cleanup_temp_files(self):
        """Remove old files from transient directories."""
        logger.info("Cleaning up old files...")
        for d in [self.msg_dir, self.audio_dir]:
            if os.path.exists(d):
                for f in os.listdir(d):
                    try: 
                        # Mandatory for Windows: check if it's an mp3 and ensure mixer is unloaded elsewhere
                        os.remove(os.path.join(d, f))
                    except Exception as e: 
                        logger.debug(f"Could not remove {f}: {e}")

    def extract_video_id(self, url_or_id: str) -> str:
        """Extract YouTube video ID from URL or return raw ID."""
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

    def _process_message(self, data: Any) -> Optional[str]:
        """Filter, translate and format the incoming message."""
        if isinstance(data, str):
            return data
            
        author = data.get("author", "Unknown")
        message = data.get("message", "")

        # Profanity Filter
        if self.profanity_enabled:
            msg_lower = message.lower()
            for word in self.profanity_list:
                if word in msg_lower:
                    logger.warning(f"Message from {author} blocked by profanity filter.")
                    return None

        # Length Filter
        if len(message) > 200:
            logger.warning(f"Message too long from {author}, skipped.")
            return None

        # Duplicate Filter
        msg_id = f"{author}:{message}"
        if msg_id in self.seen_messages:
            return None
        
        self.seen_messages.add(msg_id)
        if len(self.seen_messages) > self.max_seen_messages:
            self.seen_messages.clear()
            
        # Translation
        if self.auto_translate:
            try:
                # Basic Thai detection
                if not any('\u0e00' <= char <= '\u0e7f' for char in message):
                    translated = self.translator.translate(message)
                    logger.info(f"Translated: {message} -> {translated}")
                    message = translated
            except Exception as te:
                logger.error(f"Translation Error: {te}")
        
        return f"{author} พูดว่า {message}"

    async def _generate_audio(self, text: str, path: str):
        """Generate audio file using edge-tts or gTTS fallback."""
        try:
            await edge_tts.Communicate(text, self.voice).save(path)
        except Exception as e:
            logger.warning(f"edge-tts failed, using gTTS fallback: {e}")
            try:
                lang_code = self.voice.split('-')[0] if '-' in self.voice else 'th'
                tts = gTTS(text=text, lang=lang_code)
                tts.save(path)
            except Exception as ge:
                logger.error(f"gTTS fallback also failed: {ge}")
                raise ge

    async def generator_task(self, session_id: int):
        """Main generator loop: process messages and generate audio."""
        logger.info(f"Generator started (Session: {session_id}, Voice: {self.voice})")
        while self.is_running and session_id == self.current_session_id:
            try:
                try:
                    data = self.msg_queue.get(timeout=0.2)
                except queue.Empty:
                    continue

                processed_text = self._process_message(data)
                if not processed_text:
                    continue

                logger.info(f"Processing: {processed_text}")
                path = os.path.join(self.audio_dir, f"{int(time.time()*1000)}.mp3")
                
                try:
                    await self._generate_audio(processed_text, path)
                    # Double check session before putting to queue
                    if self.is_running and session_id == self.current_session_id:
                        self.audio_queue.put((path, len(processed_text)), timeout=1.0)
                    else:
                        if os.path.exists(path): os.remove(path)
                except queue.Full:
                    logger.warning("Audio queue full, dropping message.")
                    if os.path.exists(path): os.remove(path)
                except Exception as ge:
                    logger.error(f"Audio Generation Error: {ge}")
                    continue

            except Exception as e:
                logger.error(f"Generator Error: {e}")
                await asyncio.sleep(1)
        logger.info(f"Generator stopped (Session: {session_id})")

    def player_loop(self, session_id: int):
        """Main player loop: play generated audio files."""
        logger.info(f"Player started (Session: {session_id})")
        while self.is_running and session_id == self.current_session_id:
            try:
                try:
                    path, char_count = self.audio_queue.get(timeout=0.2)
                except queue.Empty:
                    continue

                if os.path.exists(path):
                    try:
                        logger.info(f"Playing: {path}")
                        mixer.music.load(path)
                        mixer.music.play()
                        while mixer.music.get_busy() and self.is_running and session_id == self.current_session_id:
                            time.sleep(0.1)
                        mixer.music.unload()
                        
                        # Apply delay per character
                        time.sleep(min(char_count * self.delay_per_char, self.max_delay))
                    except Exception as e: 
                        logger.error(f"Play Error: {e}")
                    finally:
                        try:
                            if os.path.exists(path): os.remove(path)
                        except: pass
            except Exception as e: 
                logger.error(f"Player Loop Error: {e}")
        logger.info(f"Player stopped (Session: {session_id})")

    def start(self, config_dict: Dict[str, Any]):
        """Initialize and start all engine components and collectors."""
        if self.is_running: 
            self.stop()
            time.sleep(0.2) # Small cooldown for old threads to see the flag
            
        self.is_running = True
        self.current_session_id += 1
        current_sid = self.current_session_id
        
        # Load Config
        self.voice = config_dict.get("voice", "th-TH-PremwadeeNeural")
        self.delay_per_char = float(config_dict.get("delay_per_char", 0.03))
        self.max_delay = float(config_dict.get("max_delay", 2.0))
        self.auto_translate = str(config_dict.get("auto_translate")) == "True"
        self.profanity_enabled = str(config_dict.get("profanity_enabled")) == "True"
        
        logger.info(f"Starting Engine Session {current_sid}...")
        logger.info(f"Config: Voice={self.voice}, AutoTranslate={self.auto_translate}, Profanity={self.profanity_enabled}")

        def run_engine():
            try:
                self._clear_queues()
                self._cleanup_temp_files()
                self._load_profanity_list()
                
                # Core Threads
                self.threads = [
                    threading.Thread(target=lambda: asyncio.run(self.generator_task(current_sid)), daemon=True),
                    threading.Thread(target=lambda: self.player_loop(current_sid), daemon=True)
                ]

                # Collectors check session as well
                is_running_check = lambda: self.is_running and current_sid == self.current_session_id
                
                if str(config_dict.get("yt_enabled")) == "True" and config_dict.get("yt_id"):
                    vid = self.extract_video_id(config_dict.get("yt_id", ""))
                    self.threads.append(threading.Thread(
                        target=youtube_collector, 
                        args=(vid, self.msg_queue, is_running_check), 
                        daemon=True
                    ))
                    
                if str(config_dict.get("tw_enabled")) == "True" and config_dict.get("tw_channel"):
                    channel = config_dict.get("tw_channel", "")
                    self.threads.append(threading.Thread(
                        target=twitch_collector, 
                        args=(channel, self.msg_queue, is_running_check), 
                        daemon=True
                    ))

                if str(config_dict.get("tk_enabled")) == "True" and config_dict.get("tk_username"):
                    username = config_dict.get("tk_username", "")
                    self.threads.append(threading.Thread(
                        target=tiktok_collector, 
                        args=(username, self.msg_queue, is_running_check), 
                        daemon=True
                    ))

                for t in self.threads: t.start()
                logger.info(f"Engine session {current_sid} started with {len(self.threads)-2} collectors")
            except Exception as e:
                logger.error(f"Failed to start engine: {e}\n{traceback.format_exc()}")
                self.is_running = False

        threading.Thread(target=run_engine, daemon=True).start()

    def stop(self):
        """Stop all engine components."""
        self.is_running = False
        self.current_session_id += 1 # Invalidate current session
        self.threads = []
        try:
            mixer.music.stop()
            mixer.music.unload()
        except: pass
        logger.info("Engine stop signal sent.")

    def update_config(self, config_dict: Dict[str, Any]):
        """Update engine configuration in real-time."""
        try:
            if "voice" in config_dict:
                self.voice = config_dict["voice"]
            if "delay_per_char" in config_dict:
                self.delay_per_char = float(config_dict.get("delay_per_char", 0.03))
            if "max_delay" in config_dict:
                self.max_delay = float(config_dict.get("max_delay", 2.0))
            if "auto_translate" in config_dict:
                self.auto_translate = str(config_dict["auto_translate"]) == "True"
            if "profanity_enabled" in config_dict:
                self.profanity_enabled = str(config_dict["profanity_enabled"]) == "True"
                if self.profanity_enabled:
                    self._load_profanity_list()
            logger.info("Engine configuration updated in real-time.")
        except Exception as e:
            logger.error(f"Failed to update config in real-time: {e}")

