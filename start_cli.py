import sys
import os
import time
import configparser
import traceback
import logging

# Add core directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from core.tts_engine import ChatTTSEngine
from core.app_logger import get_logger, logger as base_logger

# Setup Console Logging for CLI
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s', datefmt='%H:%M:%S'))
console_handler.setLevel(logging.INFO)
base_logger.addHandler(console_handler)

logger = get_logger("CLI")
CONFIG_FILE = "config.ini"

def load_config():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE, encoding="utf-8")
    
    if "settings" not in config:
        config.add_section("settings")
        
    return config

def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            config.write(f)
    except Exception as e:
        logger.error(f"Failed to save config: {e}")

def get_conf_value(config, key, default):
    return config.get("settings", key, fallback=default)

def main():
    config = load_config()
    
    # Load settings with fallbacks
    conf = {
        "yt_enabled": get_conf_value(config, "yt_enabled", "True"),
        "yt_id": get_conf_value(config, "YOUTUBE_VIDEO_ID", ""),
        "tw_enabled": get_conf_value(config, "tw_enabled", "False"),
        "tw_channel": get_conf_value(config, "tw_channel", ""),
        "tk_enabled": get_conf_value(config, "tk_enabled", "False"),
        "tk_username": get_conf_value(config, "tk_username", ""),
        "voice": get_conf_value(config, "VOICE", "th-TH-PremwadeeNeural"),
        "delay_per_char": get_conf_value(config, "delay_per_char", "0.03"),
        "max_delay": get_conf_value(config, "max_delay", "2.0"),
        "auto_translate": get_conf_value(config, "auto_translate", "False"),
        "profanity_enabled": get_conf_value(config, "profanity_enabled", "False")
    }
    
    # Prompt for missing required info if enabled
    needs_save = False
    
    if conf["yt_enabled"] == "True" and not conf["yt_id"]:
        conf["yt_id"] = input("Enter YouTube Video ID or URL: ").strip()
        config.set("settings", "YOUTUBE_VIDEO_ID", conf["yt_id"])
        needs_save = True

    if conf["tw_enabled"] == "True" and not conf["tw_channel"]:
        conf["tw_channel"] = input("Enter Twitch Channel Name: ").strip()
        config.set("settings", "tw_channel", conf["tw_channel"])
        needs_save = True

    if conf["tk_enabled"] == "True" and not conf["tk_username"]:
        conf["tk_username"] = input("Enter TikTok Username: ").strip()
        config.set("settings", "tk_username", conf["tk_username"])
        needs_save = True

    if needs_save:
        save_config(config)

    # Display status
    print("\n" + "="*50)
    print("   CHAT-TO-SPEECH SYSTEM (CLI MODE)")
    print("="*50)
    print(f" Platforms:")
    print(f"  - YouTube: {'ENABLED (' + conf['yt_id'] + ')' if conf['yt_enabled'] == 'True' else 'Disabled'}")
    print(f"  - Twitch:  {'ENABLED (#' + conf['tw_channel'] + ')' if conf['tw_enabled'] == 'True' else 'Disabled'}")
    print(f"  - TikTok:  {'ENABLED (@' + conf['tk_username'] + ')' if conf['tk_enabled'] == 'True' else 'Disabled'}")
    print(f" Settings:")
    print(f"  - Voice:          {conf['voice']}")
    print(f"  - Auto Translate: {conf['auto_translate']}")
    print(f"  - Profanity Filt: {conf['profanity_enabled']}")
    print("="*50)
    print(" Press Ctrl+C to stop the system.\n")

    engine = ChatTTSEngine()
    
    try:
        engine.start(conf)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping system...")
        logger.info("Stopping system via KeyboardInterrupt...")
    except Exception as e:
        logger.critical(f"Unexpected fatal error: {e}\n{traceback.format_exc()}")
    finally:
        engine.stop()
        logger.info("System stopped.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Critical startup error: {e}")
        time.sleep(5)
