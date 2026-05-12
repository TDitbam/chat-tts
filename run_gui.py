import customtkinter as ctk
import configparser
import sys
import os
import time
from engine import ChatTTSEngine

CONFIG_FILE = "config.ini"

class ChatTTSGui(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Chat TTS Controller")
        self.geometry("500x480") # เพิ่มความสูงเล็กน้อย
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.engine = ChatTTSEngine()
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_FILE, encoding="utf-8")

        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_box.insert("end", f"[{timestamp}] {message}\n")
        self.log_box.see("end")

    def create_widgets(self):
        self.label_title = ctk.CTkLabel(self, text="YouTube Chat TTS", font=("Helvetica", 24, "bold"))
        self.label_title.pack(pady=(20, 10))

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

        # Delay Per Char (เพิ่มกลับมา)
        ctk.CTkLabel(self.settings_frame, text="Delay Per Char:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.entry_delay_char = ctk.CTkEntry(self.settings_frame, width=100)
        self.entry_delay_char.insert(0, self.config.get("settings", "delay_per_char", fallback="0.03"))
        self.entry_delay_char.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # Max Delay (เพิ่มกลับมา)
        ctk.CTkLabel(self.settings_frame, text="Max Delay:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.entry_max_delay = ctk.CTkEntry(self.settings_frame, width=100)
        self.entry_max_delay.insert(0, self.config.get("settings", "max_delay", fallback="2.0"))
        self.entry_max_delay.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        self.label_status = ctk.CTkLabel(self, text="Status: Stopped", text_color="red")
        self.label_status.pack(pady=5)

        self.btn_toggle = ctk.CTkButton(self, text="Start System", command=self.toggle_system, fg_color="green", hover_color="#006400")
        self.btn_toggle.pack(pady=10)

        self.log_box = ctk.CTkTextbox(self, height=100, width=450)
        self.log_box.pack(pady=(10, 20))

    def save_settings(self):
        if not self.config.has_section("settings"): self.config.add_section("settings")
        self.config.set("settings", "YOUTUBE_VIDEO_ID", self.entry_url.get())
        self.config.set("settings", "VOICE", self.voice_var.get())
        self.config.set("settings", "delay_per_char", self.entry_delay_char.get())
        self.config.set("settings", "max_delay", self.entry_max_delay.get())
        with open(CONFIG_FILE, "w", encoding="utf-8") as f: self.config.write(f)

    def toggle_system(self):
        if not self.engine.is_running:
            self.save_settings()
            try:
                d_char = float(self.entry_delay_char.get())
                m_delay = float(self.entry_max_delay.get())
            except:
                d_char = 0.03
                m_delay = 2.0
                
            self.engine.start(self.entry_url.get(), self.voice_var.get(), d_char, m_delay)
            self.btn_toggle.configure(text="Stop System", fg_color="red", hover_color="#8B0000")
            self.label_status.configure(text="Status: Running", text_color="green")
            self.log("System started.")
        else:
            self.engine.stop()
            self.btn_toggle.configure(text="Start System", fg_color="green", hover_color="#006400")
            self.label_status.configure(text="Status: Stopped", text_color="red")
            self.log("System stopped.")

    def on_closing(self):
        self.engine.stop()
        self.destroy()
        sys.exit(0)

if __name__ == "__main__":
    app = ChatTTSGui()
    app.mainloop()
