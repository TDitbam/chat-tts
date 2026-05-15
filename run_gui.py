import customtkinter as ctk
import configparser
import sys
import os
import time
import logging
from engine import ChatTTSEngine
from logger import get_logger, logger as base_logger

logger = get_logger("GUI")
CONFIG_FILE = "config.ini"

class GuiLogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state="normal")
            self.text_widget.insert("end", msg + "\n")
            self.text_widget.see("end")
            self.text_widget.configure(state="disabled")
        self.text_widget.after(0, append)

class ChatTTSGui(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Chat TTS Multi-Platform")
        self.geometry("600x750")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.engine = ChatTTSEngine()
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_FILE, encoding="utf-8")

        self.create_widgets()
        
        # Setup Logger Redirect
        self.log_handler = GuiLogHandler(self.log_box)
        self.log_handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s', datefmt='%H:%M:%S'))
        base_logger.addHandler(self.log_handler)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        logger.info("GUI Initialized")

    def create_widgets(self):
        self.label_title = ctk.CTkLabel(self, text="Multi-Platform Chat TTS", font=("Helvetica", 24, "bold"))
        self.label_title.pack(pady=(20, 10))

        # Main Scrollable Frame
        self.main_frame = ctk.CTkScrollableFrame(self, width=550, height=450)
        self.main_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Platform Toggles Section
        self.yt_enabled = ctk.StringVar(value=self.config.get("settings", "yt_enabled", fallback="True"))
        self.fb_enabled = ctk.StringVar(value=self.config.get("settings", "fb_enabled", fallback="False"))
        self.tw_enabled = ctk.StringVar(value=self.config.get("settings", "tw_enabled", fallback="False"))
        self.tk_enabled = ctk.StringVar(value=self.config.get("settings", "tk_enabled", fallback="False"))

        # --- YouTube Section ---
        self.yt_frame = ctk.CTkFrame(self.main_frame)
        self.yt_frame.pack(pady=5, padx=10, fill="x")
        ctk.CTkCheckBox(self.yt_frame, text="YouTube Enabled", variable=self.yt_enabled, onvalue="True", offvalue="False").pack(side="left", padx=10)
        self.entry_yt = ctk.CTkEntry(self.yt_frame, placeholder_text="YouTube URL/ID", width=250)
        self.entry_yt.insert(0, self.config.get("settings", "YOUTUBE_VIDEO_ID", fallback=""))
        self.entry_yt.pack(side="right", padx=10, pady=5)

        # --- Facebook Section ---
        self.fb_frame = ctk.CTkFrame(self.main_frame)
        self.fb_frame.pack(pady=5, padx=10, fill="x")
        ctk.CTkCheckBox(self.fb_frame, text="Facebook Enabled", variable=self.fb_enabled, onvalue="True", offvalue="False").pack(side="left", padx=10)
        self.entry_fb = ctk.CTkEntry(self.fb_frame, placeholder_text="Facebook Live URL", width=250)
        self.entry_fb.insert(0, self.config.get("settings", "fb_url", fallback=""))
        self.entry_fb.pack(side="right", padx=10, pady=5)

        # --- Twitch Section ---
        self.tw_frame = ctk.CTkFrame(self.main_frame)
        self.tw_frame.pack(pady=5, padx=10, fill="x")
        ctk.CTkCheckBox(self.tw_frame, text="Twitch Enabled", variable=self.tw_enabled, onvalue="True", offvalue="False").pack(side="left", padx=10)
        self.entry_tw = ctk.CTkEntry(self.tw_frame, placeholder_text="Twitch Channel Name", width=250)
        self.entry_tw.insert(0, self.config.get("settings", "tw_channel", fallback=""))
        self.entry_tw.pack(side="right", padx=10, pady=5)

        # --- TikTok Section ---
        self.tk_frame = ctk.CTkFrame(self.main_frame)
        self.tk_frame.pack(pady=5, padx=10, fill="x")
        ctk.CTkCheckBox(self.tk_frame, text="TikTok Enabled", variable=self.tk_enabled, onvalue="True", offvalue="False").pack(side="left", padx=10)
        self.entry_tk = ctk.CTkEntry(self.tk_frame, placeholder_text="TikTok Username (@name)", width=250)
        self.entry_tk.insert(0, self.config.get("settings", "tk_username", fallback=""))
        self.entry_tk.pack(side="right", padx=10, pady=5)

        # --- General Settings ---
        self.gen_frame = ctk.CTkFrame(self.main_frame)
        self.gen_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(self.gen_frame, text="Voice:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.voice_var = ctk.StringVar(value=self.config.get("settings", "VOICE", fallback="th-TH-PremwadeeNeural"))
        self.voice_menu = ctk.CTkOptionMenu(self.gen_frame, values=["th-TH-PremwadeeNeural", "th-TH-NiwatNeural"], variable=self.voice_var)
        self.voice_menu.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(self.gen_frame, text="Delay Per Char:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.entry_delay_char = ctk.CTkEntry(self.gen_frame, width=100)
        self.entry_delay_char.insert(0, self.config.get("settings", "delay_per_char", fallback="0.03"))
        self.entry_delay_char.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(self.gen_frame, text="Max Delay:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.entry_max_delay = ctk.CTkEntry(self.gen_frame, width=100)
        self.entry_max_delay.insert(0, self.config.get("settings", "max_delay", fallback="2.0"))
        self.entry_max_delay.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.label_status = ctk.CTkLabel(self, text="Status: Stopped", text_color="red")
        self.label_status.pack(pady=5)

        self.btn_toggle = ctk.CTkButton(self, text="Start System", command=self.toggle_system, fg_color="green", hover_color="#006400")
        self.btn_toggle.pack(pady=10)

        self.log_box = ctk.CTkTextbox(self, height=150, width=550)
        self.log_box.pack(pady=(10, 20))
        self.log_box.configure(state="disabled")

    def save_settings(self):
        if not self.config.has_section("settings"): self.config.add_section("settings")
        self.config.set("settings", "yt_enabled", self.yt_enabled.get())
        self.config.set("settings", "fb_enabled", self.fb_enabled.get())
        self.config.set("settings", "tw_enabled", self.tw_enabled.get())
        self.config.set("settings", "tk_enabled", self.tk_enabled.get())
        self.config.set("settings", "YOUTUBE_VIDEO_ID", self.entry_yt.get())
        self.config.set("settings", "fb_url", self.entry_fb.get())
        self.config.set("settings", "tw_channel", self.entry_tw.get())
        self.config.set("settings", "tk_username", self.entry_tk.get())
        self.config.set("settings", "VOICE", self.voice_var.get())
        self.config.set("settings", "delay_per_char", self.entry_delay_char.get())
        self.config.set("settings", "max_delay", self.entry_max_delay.get())
        with open(CONFIG_FILE, "w", encoding="utf-8") as f: self.config.write(f)

    def toggle_system(self):
        if not self.engine.is_running:
            self.save_settings()
            conf = {
                "yt_enabled": self.yt_enabled.get(),
                "yt_id": self.entry_yt.get(),
                "fb_enabled": self.fb_enabled.get(),
                "fb_url": self.entry_fb.get(),
                "tw_enabled": self.tw_enabled.get(),
                "tw_channel": self.entry_tw.get(),
                "tk_enabled": self.tk_enabled.get(),
                "tk_username": self.entry_tk.get(),
                "voice": self.voice_var.get(),
                "delay_per_char": self.entry_delay_char.get(),
                "max_delay": self.entry_max_delay.get()
            }
            self.engine.start(conf)
            self.btn_toggle.configure(text="Stop System", fg_color="red", hover_color="#8B0000")
            self.label_status.configure(text="Status: Running", text_color="green")
        else:
            self.engine.stop()
            self.btn_toggle.configure(text="Start System", fg_color="green", hover_color="#006400")
            self.label_status.configure(text="Status: Stopped", text_color="red")

    def on_closing(self):
        self.engine.stop()
        self.destroy()
        sys.exit(0)

if __name__ == "__main__":
    app = ChatTTSGui()
    app.mainloop()
