import configparser
import tkinter as tk
from tkinter import messagebox

CONFIG_FILE = "config.ini"

def load_config():
    config = configparser.ConfigParser()
    if not config.read(CONFIG_FILE, encoding="utf-8"):
        config["settings"] = {
            "YOUTUBE_VIDEO_ID": "",
            "DELAY_PER_CHAR": "0.03",
            "MAX_DELAY": "2.0"
        }
    return config

def save_config():
    try:
        config["settings"]["YOUTUBE_VIDEO_ID"] = entry_video_id.get().strip()
        config["settings"]["DELAY_PER_CHAR"] = entry_delay.get().strip()
        config["settings"]["MAX_DELAY"] = entry_max_delay.get().strip()

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            config.write(f)

        messagebox.showinfo("Success", "บันทึกเรียบร้อย")
    except Exception as e:
        messagebox.showerror("Error", str(e))

config = load_config()

root = tk.Tk()
root.title("Config Editor")
root.geometry("400x260")

tk.Label(root, text="YouTube Video ID / URL").pack()
entry_video_id = tk.Entry(root, width=40)
entry_video_id.pack()
entry_video_id.insert(0, config["settings"].get("YOUTUBE_VIDEO_ID", ""))

tk.Label(root, text="Delay per char").pack()
entry_delay = tk.Entry(root, width=40)
entry_delay.pack()
entry_delay.insert(0, config["settings"].get("DELAY_PER_CHAR", ""))

tk.Label(root, text="Max delay").pack()
entry_max_delay = tk.Entry(root, width=40)
entry_max_delay.pack()
entry_max_delay.insert(0, config["settings"].get("MAX_DELAY", ""))

tk.Button(root, text="Save", command=save_config, bg="green", fg="white").pack(pady=10)

root.mainloop()