import subprocess
import time
import sys
import os

# ชื่อไฟล์สคริปต์หลัก
TARGET_SCRIPT = "main.py"

def run_target():
    # 0x08000000 = CREATE_NO_WINDOW (ห้ามเปิดหน้าต่างใหม่)
    return subprocess.Popen(
        [sys.executable, TARGET_SCRIPT],
        creationflags=0x08000000 if os.name == 'nt' else 0
    )

def monitor():
    print(f"[{time.strftime('%H:%M:%S')}] 🛡️ Watcher Active: Monitoring {TARGET_SCRIPT}")
    process = run_target()

    while True:
        # ตรวจสอบสถานะ Process ทุก 5 วินาที
        if process.poll() is not None:
            print(f"[{time.strftime('%H:%M:%S')}] ⚠️ Main script stopped. Restarting silently...")
            time.sleep(2)
            process = run_target()
        time.sleep(5)

if __name__ == "__main__":
    try:
        monitor()
    except KeyboardInterrupt:
        print("\nStopping Watcher and System...")