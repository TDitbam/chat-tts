import logging
import os
from datetime import datetime

# สร้างโฟลเดอร์ logs ถ้ายังไม่มี
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# ตั้งค่าชื่อไฟล์ log ตามวันที่
log_filename = os.path.join(LOG_DIR, f"chat_tts_{datetime.now().strftime('%Y-%m-%d')}.log")

# กำหนด Format ของ log
log_format = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')

# สร้าง Logger
logger = logging.getLogger("ChatTTS")
logger.setLevel(logging.DEBUG)

# File Handler (บันทึกลงไฟล์)
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setFormatter(log_format)
file_handler.setLevel(logging.INFO)

# Console Handler (แสดงบน Terminal)
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)
console_handler.setLevel(logging.DEBUG)

# เพิ่ม Handler เข้าไปใน Logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def get_logger(name):
    return logger.getChild(name)
