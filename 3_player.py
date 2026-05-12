import os
import time
from playsound3 import playsound

AUDIO_DIR = "temp_audio"

if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

def safe_remove(file_path, max_attempts=5):
    """พยายามลบไฟล์ซ้ำๆ กรณีที่ไฟล์ยังถูกล็อกอยู่"""
    for i in range(max_attempts):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except PermissionError:
            time.sleep(0.5) # รอ 0.5 วินาทีแล้วลองใหม่
    return False

def main():
    print("Audio Player Running...")
    while True:
        try:
            # ดึงรายชื่อไฟล์และเรียงตามชื่อ (Timestamp)
            files = sorted([f for f in os.listdir(AUDIO_DIR) if f.endswith(".mp3")])
            
            if files:
                for f in files:
                    file_path = os.path.join(AUDIO_DIR, f)
                    try:
                        print(f"Playing: {f}")
                        playsound(file_path) 
                        # หลังจากบรรทัดนี้ playsound3 ควรจะเล่นจบแบบ Synchronous
                    except Exception as e:
                        print(f"Play Error: {e}")
                    finally:
                        # ใช้ฟังก์ชันลบไฟล์แบบปลอดภัย
                        if not safe_remove(file_path):
                            print(f"Could not delete {f}, it might be locked.")
            
            time.sleep(0.1)
        except Exception as e:
            print(f"Player Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()