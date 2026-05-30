import customtkinter as ctk
import configparser
import sys
import os
import logging

# Add core directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from core.tts_engine import ChatTTSEngine
from core.app_logger import get_logger, logger as base_logger

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
        
        # Real-time listeners
        self._setup_listeners()

    def _setup_listeners(self):
        """Setup listeners for real-time config updates."""
        for var in [self.auto_translate, self.profanity_enabled, self.voice_var]:
            var.trace_add("write", lambda *args: self.apply_realtime_config())
            
        # Add focus-out listeners for Entry widgets
        self.entry_delay_char.bind("<FocusOut>", lambda e: self.apply_realtime_config())
        self.entry_max_delay.bind("<FocusOut>", lambda e: self.apply_realtime_config())
        self.entry_delay_char.bind("<Return>", lambda e: self.apply_realtime_config())
        self.entry_max_delay.bind("<Return>", lambda e: self.apply_realtime_config())

    def apply_realtime_config(self):
        """Apply current GUI settings to the engine in real-time."""
        if self.engine.is_running:
            conf = {
                "voice": self.voice_var.get(),
                "delay_per_char": self.entry_delay_char.get(),
                "max_delay": self.entry_max_delay.get(),
                "auto_translate": self.auto_translate.get(),
                "profanity_enabled": self.profanity_enabled.get()
            }
            self.engine.update_config(conf)

    def create_widgets(self):
        self.label_title = ctk.CTkLabel(self, text="Chat TTS Multi-Platform", font=("Helvetica", 24, "bold"))
        self.label_title.pack(pady=(20, 10))

        # Tabview for organization
        self.tabview = ctk.CTkTabview(self, width=550, height=400)
        self.tabview.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.tab_connect = self.tabview.add("Connections")
        self.tab_settings = self.tabview.add("System Settings")
        self.tab_filter = self.tabview.add("Profanity Filter")

        self._init_vars()
        
        # --- Connections Tab ---
        self._setup_youtube_section(self.tab_connect)
        self._setup_twitch_section(self.tab_connect)
        self._setup_tiktok_section(self.tab_connect)
        
        # --- Settings Tab ---
        self._setup_general_settings(self.tab_settings)

        # --- Filter Tab ---
        self._setup_filter_tab(self.tab_filter)

        # Bottom Area
        self.label_status = ctk.CTkLabel(self, text="Status: Stopped", text_color="red", font=("Helvetica", 14, "bold"))
        self.label_status.pack(pady=5)

        self.btn_toggle = ctk.CTkButton(self, text="START SYSTEM", command=self.toggle_system, 
                                        height=40, font=("Helvetica", 16, "bold"),
                                        fg_color="green", hover_color="#006400")
        self.btn_toggle.pack(pady=10, padx=20, fill="x")

        self.log_box = ctk.CTkTextbox(self, height=150, width=550)
        self.log_box.pack(pady=(10, 20), padx=20, fill="x")
        self.log_box.configure(state="disabled")

    def _init_vars(self):
        self.yt_enabled = ctk.StringVar(value=self.config.get("settings", "yt_enabled", fallback="True"))
        self.tw_enabled = ctk.StringVar(value=self.config.get("settings", "tw_enabled", fallback="False"))
        self.tk_enabled = ctk.StringVar(value=self.config.get("settings", "tk_enabled", fallback="False"))
        self.auto_translate = ctk.StringVar(value=self.config.get("settings", "auto_translate", fallback="False"))
        self.profanity_enabled = ctk.StringVar(value=self.config.get("settings", "profanity_enabled", fallback="False"))
        self.voice_var = ctk.StringVar(value=self.config.get("settings", "VOICE", fallback="th-TH-PremwadeeNeural"))

    def _setup_youtube_section(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(frame, text="YouTube Live", font=("Helvetica", 12, "bold")).pack(anchor="w", padx=10, pady=2)
        
        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkCheckBox(inner, text="Enabled", variable=self.yt_enabled, onvalue="True", offvalue="False").pack(side="left", padx=10)
        self.entry_yt = ctk.CTkEntry(inner, placeholder_text="Video ID or URL", width=300)
        self.entry_yt.insert(0, self.config.get("settings", "YOUTUBE_VIDEO_ID", fallback=""))
        self.entry_yt.pack(side="right", padx=10)

    def _setup_twitch_section(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(frame, text="Twitch Chat", font=("Helvetica", 12, "bold")).pack(anchor="w", padx=10, pady=2)
        
        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkCheckBox(inner, text="Enabled", variable=self.tw_enabled, onvalue="True", offvalue="False").pack(side="left", padx=10)
        self.entry_tw = ctk.CTkEntry(inner, placeholder_text="Channel Name", width=300)
        self.entry_tw.insert(0, self.config.get("settings", "tw_channel", fallback=""))
        self.entry_tw.pack(side="right", padx=10)

    def _setup_tiktok_section(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(frame, text="TikTok Live", font=("Helvetica", 12, "bold")).pack(anchor="w", padx=10, pady=2)
        
        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkCheckBox(inner, text="Enabled", variable=self.tk_enabled, onvalue="True", offvalue="False").pack(side="left", padx=10)
        self.entry_tk = ctk.CTkEntry(inner, placeholder_text="@username", width=300)
        self.entry_tk.insert(0, self.config.get("settings", "tk_username", fallback=""))
        self.entry_tk.pack(side="right", padx=10)

    def _setup_general_settings(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(frame, text="Voice & Translation Settings", font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=15)
        
        ctk.CTkCheckBox(frame, text="Auto-Translate to Thai (แปลภาษาอัตโนมัติ)", variable=self.auto_translate, onvalue="True", offvalue="False").grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="w")

        ctk.CTkLabel(frame, text="TTS Voice:").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.voice_menu = ctk.CTkOptionMenu(frame, values=["th-TH-PremwadeeNeural", "th-TH-NiwatNeural"], variable=self.voice_var, width=200)
        self.voice_menu.grid(row=2, column=1, padx=20, pady=10, sticky="w")

        ctk.CTkLabel(frame, text="Delay Per Character:").grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.entry_delay_char = ctk.CTkEntry(frame, width=100)
        self.entry_delay_char.insert(0, self.config.get("settings", "delay_per_char", fallback="0.03"))
        self.entry_delay_char.grid(row=3, column=1, padx=20, pady=10, sticky="w")

        ctk.CTkLabel(frame, text="Max Delay (seconds):").grid(row=4, column=0, padx=20, pady=10, sticky="w")
        self.entry_max_delay = ctk.CTkEntry(frame, width=100)
        self.entry_max_delay.insert(0, self.config.get("settings", "max_delay", fallback="2.0"))
        self.entry_max_delay.grid(row=4, column=1, padx=20, pady=10, sticky="w")

    def _setup_filter_tab(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(frame, text="Profanity Filter Settings (ระบบกรองคำหยาบ)", font=("Helvetica", 14, "bold")).pack(pady=10)
        
        ctk.CTkCheckBox(frame, text="Enable Profanity Filter (เปิดระบบกรองคำหยาบ)", variable=self.profanity_enabled, onvalue="True", offvalue="False").pack(pady=10, padx=20, anchor="w")
        
        ctk.CTkLabel(frame, text="Blocked Words (One per line):").pack(pady=(10, 0), padx=20, anchor="w")
        self.textbox_filter = ctk.CTkTextbox(frame, height=200)
        self.textbox_filter.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Load existing words
        if os.path.exists("bad_words.txt"):
            try:
                with open("bad_words.txt", "r", encoding="utf-8") as f:
                    self.textbox_filter.insert("1.0", f.read())
            except:
                pass

    def save_settings(self):
        if not self.config.has_section("settings"): self.config.add_section("settings")
        self.config.set("settings", "yt_enabled", self.yt_enabled.get())
        self.config.set("settings", "tw_enabled", self.tw_enabled.get())
        self.config.set("settings", "tk_enabled", self.tk_enabled.get())
        self.config.set("settings", "auto_translate", self.auto_translate.get())
        self.config.set("settings", "profanity_enabled", self.profanity_enabled.get())
        self.config.set("settings", "YOUTUBE_VIDEO_ID", self.entry_yt.get())
        self.config.set("settings", "tw_channel", self.entry_tw.get())
        self.config.set("settings", "tk_username", self.entry_tk.get())
        self.config.set("settings", "VOICE", self.voice_var.get())
        self.config.set("settings", "delay_per_char", self.entry_delay_char.get())
        self.config.set("settings", "max_delay", self.entry_max_delay.get())
        
        # Save bad words
        try:
            words = self.textbox_filter.get("1.0", "end-1c")
            with open("bad_words.txt", "w", encoding="utf-8") as f:
                f.write(words)
        except Exception as e:
            logger.error(f"Failed to save bad_words.txt: {e}")

        with open(CONFIG_FILE, "w", encoding="utf-8") as f: self.config.write(f)

    def toggle_system(self):
        if not self.engine.is_running:
            # Clear log box for new session
            self.log_box.configure(state="normal")
            self.log_box.delete("1.0", "end")
            self.log_box.configure(state="disabled")
            
            self.save_settings()
            conf = {
                "yt_enabled": self.yt_enabled.get(),
                "yt_id": self.entry_yt.get(),
                "tw_enabled": self.tw_enabled.get(),
                "tw_channel": self.entry_tw.get(),
                "tk_enabled": self.tk_enabled.get(),
                "tk_username": self.entry_tk.get(),
                "voice": self.voice_var.get(),
                "delay_per_char": self.entry_delay_char.get(),
                "max_delay": self.entry_max_delay.get(),
                "auto_translate": self.auto_translate.get(),
                "profanity_enabled": self.profanity_enabled.get()
            }
            self.engine.start(conf)
            self.btn_toggle.configure(text="STOP SYSTEM", fg_color="red", hover_color="#8B0000")
            self.label_status.configure(text="Status: Running", text_color="green")
        else:
            self.engine.stop()
            self.btn_toggle.configure(text="START SYSTEM", fg_color="green", hover_color="#006400")
            self.label_status.configure(text="Status: Stopped", text_color="red")


    def on_closing(self):
        self.engine.stop()
        self.destroy()
        sys.exit(0)

if __name__ == "__main__":
    app = ChatTTSGui()
    app.mainloop()
