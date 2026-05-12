import multiprocessing
import subprocess
import sys
import time

def run_script(script_name):
    """ฟังก์ชันสำหรับรัน script แยก process"""
    print(f"Starting {script_name}...")
    try:
        # ใช้ sys.executable เพื่อเรียกใช้ python ตัวเดียวกันกับที่รัน script นี้
        subprocess.check_call([sys.executable, script_name])
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error in {script_name}: {e}")

if __name__ == "__main__":
    # รายชื่อสคริปต์ที่ต้องการรัน
    scripts = ["1_collector.py", "2_generator.py", "3_player.py"]
    processes = []

    print("--- Chat TTS System Starting ---")

    try:
        # เริ่มรันแต่ละสคริปต์ใน Process ของตัวเอง
        for script in scripts:
            p = multiprocessing.Process(target=run_script, args=(script,))
            p.start()
            processes.append(p)
            time.sleep(1) # หน่วงเวลานิดหน่อยเพื่อให้แต่ละตัวตั้งตัวทัน

        print("System is running. Press Ctrl+C to stop all processes.")
        
        # รอให้ทุก process ทำงานไปเรื่อยๆ
        for p in processes:
            p.join()

    except KeyboardInterrupt:
        print("\nStopping system...")
        for p in processes:
            p.terminate()
            p.join()
        print("All processes stopped.")
