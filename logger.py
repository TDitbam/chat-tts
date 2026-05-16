import logging
import os
from datetime import datetime

# สร้างโฟลเดอร์ logs ถ้ายังไม่มี
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# ตั้งค่าชื่อไฟล์ log ตามวันที่
log_filename = os.path.join(LOG_DIR, f"chat_tts_{datetime.now().strftime('%Y-%m-%d')}.log")
static_log_filename = os.path.join(LOG_DIR, "log.txt")

# กำหนด Format ของ log
log_format = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')

# สร้าง Logger
logger = logging.getLogger("ChatTTS")
logger.setLevel(logging.DEBUG)

# File Handler (บันทึกลงไฟล์ตามวันที่)
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setFormatter(log_format)
file_handler.setLevel(logging.INFO)

# Static File Handler (บันทึกลง log.txt เสมอ)
static_file_handler = logging.FileHandler(static_log_filename, mode='w', encoding='utf-8')
static_file_handler.setFormatter(log_format)
static_file_handler.setLevel(logging.DEBUG)

# Platform-specific File Handlers
def create_platform_handler(platform):
    handler = logging.FileHandler(os.path.join(LOG_DIR, f"{platform}.txt"), mode='w', encoding='utf-8')
    handler.setFormatter(log_format)
    handler.setLevel(logging.DEBUG)
    return handler

yt_handler = create_platform_handler("youtube")
tk_handler = create_platform_handler("tiktok")
fb_handler = create_platform_handler("facebook")
tw_handler = create_platform_handler("twitch")

# Console Handler (แสดงบน Terminal)
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)
console_handler.setLevel(logging.DEBUG)

# เพิ่ม Handler เข้าไปใน Logger
logger.addHandler(file_handler)
logger.addHandler(static_file_handler)
logger.addHandler(console_handler)

def get_logger(name):
    child_logger = logger.getChild(name)
    
    # Assign specific handlers based on name
    if "YouTube" in name:
        child_logger.addHandler(yt_handler)
        child_logger.propagate = False # Prevent double logging to main log.txt/console if preferred, 
                                       # but here we keep it True to have everything in main too.
    elif "TikTok" in name:
        child_logger.addHandler(tk_handler)
    elif "Facebook" in name:
        child_logger.addHandler(fb_handler)
    elif "Twitch" in name:
        child_logger.addHandler(tw_handler)
        
    return child_logger
