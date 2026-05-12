import customtkinter as ctk
import configparser
import subprocess
import sys
import os
import threading
import time

CONFIG_FILE = "config.ini"

class ChatTTSGui(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Chat TTS Controller")
        self.geometry("500x400")
        
        # ตั้งค่าธีม
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ตัวแปรสถานะ
        self.processes = []
        self.is_running = False

        # โหลด Config
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_FILE, encoding="utf-8")

        # สร้าง UI
        self.create_widgets()

    def create_widgets(self):
        # ส่วนหัว
        self.label_title = ctk.CTkLabel(self, text="YouTube Chat TTS", font=("Helvetica", 24, "bold"))
        self.label_title.pack(pady=(20, 10))

        # --- Settings Area (Scrollable or Frame) ---
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # YouTube Video ID
        ctk.CTkLabel(self.settings_frame, text="YouTube URL/ID:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.entry_url = ctk.CTkEntry(self.settings_frame, width=250)
        self.entry_url.insert(0, self.config.get("settings", "YOUTUBE_VIDEO_ID", fallback=""))
        self.entry_url.grid(row=0, column=1, padx=10, pady=5)

        # Voice Selection
        ctk.CTkLabel(self.settings_frame, text="Voice:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.voice_var = ctk.StringVar(value=self.config.get("settings", "VOICE", fallback="th-TH-PremwadeeNeural"))
        self.voice_menu = ctk.CTkOptionMenu(self.settings_frame, values=["th-TH-PremwadeeNeural", "th-TH-NiwatNeural"], variable=self.voice_var)
        self.voice_menu.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Delay Per Char
        ctk.CTkLabel(self.settings_frame, text="Delay Per Char:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.entry_delay_char = ctk.CTkEntry(self.settings_frame, width=100)
        self.entry_delay_char.insert(0, self.config.get("settings", "delay_per_char", fallback="0.03"))
        self.entry_delay_char.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # Max Delay
        ctk.CTkLabel(self.settings_frame, text="Max Delay:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.entry_max_delay = ctk.CTkEntry(self.settings_frame, width=100)
        self.entry_max_delay.insert(0, self.config.get("settings", "max_delay", fallback="2.0"))
        self.entry_max_delay.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # --- Control Area ---
        self.label_status = ctk.CTkLabel(self, text="Status: Stopped", text_color="red")
        self.label_status.pack(pady=5)

        self.btn_toggle = ctk.CTkButton(self, text="Start System", command=self.toggle_system, fg_color="green", hover_color="#006400")
        self.btn_toggle.pack(pady=10)

        self.btn_save = ctk.CTkButton(self, text="Save Settings", command=self.save_settings, fg_color="gray")
        self.btn_save.pack(pady=5)

        self.log_box = ctk.CTkTextbox(self, height=80, width=450)
        self.log_box.pack(pady=(10, 20))
        self.log_box.insert("0.0", "Welcome to Chat TTS Controller\n")

    def save_settings(self):
        if not self.config.has_section("settings"):
            self.config.add_section("settings")
        
        self.config.set("settings", "YOUTUBE_VIDEO_ID", self.entry_url.get())
        self.config.set("settings", "VOICE", self.voice_var.get())
        self.config.set("settings", "delay_per_char", self.entry_delay_char.get())
        self.config.set("settings", "max_delay", self.entry_max_delay.get())
        
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            self.config.write(f)
        self.log("Settings saved and updated in config.ini.")

    def toggle_system(self):
        if not self.is_running:
            self.start_system()
        else:
            self.stop_system()

    def start_system(self):
        self.save_settings() # บันทึกก่อนรัน
        self.is_running = True
        self.btn_toggle.configure(text="Stop System", fg_color="red", hover_color="#8B0000")
        self.label_status.configure(text="Status: Running", text_color="green")
        
        # ล้างไฟล์เก่าๆ เพื่อความสะอาด
        for d in ["msg_queue", "temp_audio"]:
            if os.path.exists(d):
                for f in os.listdir(d):
                    try:
                        os.remove(os.path.join(d, f))
                    except: pass

        # รันสคริปต์ใน Thread แยกเพื่อไม่ให้ GUI ค้าง
        self.thread = threading.Thread(target=self.run_all_processes, daemon=True)
        self.thread.start()
        self.log("System started.")

    def run_all_processes(self):
        scripts = ["1_collector.py", "2_generator.py", "3_player.py"]
        self.processes = []
        
        for script in scripts:
            if not self.is_running: break
            
            p = subprocess.Popen([sys.executable, script])
            self.processes.append(p)
            self.log(f"Started {script}")
            time.sleep(1)

    def stop_system(self):
        self.is_running = False
        self.btn_toggle.configure(text="Start System", fg_color="green", hover_color="#006400")
        self.label_status.configure(text="Status: Stopped", text_color="red")
        
        for p in self.processes:
            p.terminate()
        
        self.processes = []
        self.log("System stopped.")

if __name__ == "__main__":
    app = ChatTTSGui()
    app.mainloop()
