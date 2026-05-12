import os
import time
from playsound3 import playsound

def main():
    print("Player Running...")
    while True:
        try:
            files = sorted([f for f in os.listdir("temp_audio") if f.endswith(".mp3")])
            for f in files:
                path = os.path.join("temp_audio", f)
                try:
                    playsound(path)
                    os.remove(path)
                except: pass
        except: pass
        time.sleep(0.2)

if __name__ == "__main__":
    main()
