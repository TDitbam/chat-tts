import logging
import os
import sys
from datetime import datetime

def get_app_dir():
    # ถ้าเป็น .exe ให้ใช้ AppData, ถ้าเป็น script ให้ใช้ที่เดิม
    if getattr(sys, 'frozen', False):
        app_dir = os.path.join(os.getenv('APPDATA'), 'ChatTTS')
    else:
        app_dir = os.getcwd()
    
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
    return app_dir

# สร้างโฟลเดอร์ logs ถ้ายังไม่มี
LOG_DIR = os.path.join(get_app_dir(), "logs")
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
tw_handler = create_platform_handler("twitch")

# เพิ่ม Handler เข้าไปใน Logger (ถอด console_handler ออกตามคำขอ)
logger.addHandler(file_handler)
logger.addHandler(static_file_handler)

def get_logger(name):
    child_logger = logger.getChild(name)
    
    # Assign specific handlers based on name
    if "YouTube" in name:
        child_logger.addHandler(yt_handler)
    elif "TikTok" in name:
        child_logger.addHandler(tk_handler)
    elif "Twitch" in name:
        child_logger.addHandler(tw_handler)
        
    return child_logger
