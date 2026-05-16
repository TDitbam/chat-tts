import os
import sys
import platform
from datetime import datetime

# Use importlib.metadata for Python 3.8+
if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    metadata = None

# Configuration
LOG_DIR = "logs"
FILES_TO_DIAGNOSE = [
    "engine.py",
    "youtube_collector.py",
    "facebook_collector.py",
    "twitch_collector.py",
    "tiktok_collector.py",
    "logger.py"
]

def get_lib_version(name):
    if metadata:
        try:
            return metadata.version(name)
        except metadata.PackageNotFoundError:
            return "Not Installed"
    return "Unknown (Python < 3.8)"

def generate_report():
    report = []
    report.append("=== AI DIAGNOSTIC REPORT ===")
    report.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"OS: {platform.system()} {platform.release()}")
    report.append(f"Python: {sys.version}")
    
    report.append("\n--- Library Versions ---")
    libs = ["chat-downloader", "TikTokLive", "twitchio", "pytchat", "edge-tts", "playsound3"]
    for lib in libs:
        report.append(f"{lib}: {get_lib_version(lib)}")
    
    report.append("\n--- Platform Status (Latest Logs) ---")
    platforms = ["youtube", "facebook", "twitch", "tiktok", "log"]
    for p in platforms:
        log_path = os.path.join(LOG_DIR, f"{p}.txt")
        if p == "log": log_path = os.path.join(LOG_DIR, "log.txt")
        
        report.append(f"\n[{p.upper()}]")
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                # Get last 5 lines for summary
                last_lines = lines[-5:] if len(lines) > 5 else lines
                if not last_lines:
                    report.append("No logs recorded.")
                else:
                    for line in last_lines:
                        report.append(line.strip())
        else:
            report.append("Log file not found.")

    report.append("\n--- Active Files ---")
    for f in FILES_TO_DIAGNOSE:
        if os.path.exists(f):
            report.append(f"[OK] {f}")
        else:
            report.append(f"[MISSING] {f}")

    report.append("\n=== END OF REPORT ===")
    report.append("AI Instruction: Please analyze the errors above and suggest fixes for the specific platform files.")
    
    return "\n".join(report)

if __name__ == "__main__":
    print("Generating AI Diagnostic Report...")
    report_content = generate_report()
    
    # Save to a file for easy sharing
    with open("ai_report.txt", "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print("\n" + report_content)
    print("\n[SUCCESS] Report saved to 'ai_report.txt'. You can copy this content to the AI.")
