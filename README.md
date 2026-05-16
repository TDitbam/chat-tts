# Chat TTS Multi-Platform

โปรเจกต์อ่านข้อความจากไลฟ์แชทแล้วแปลงเป็นเสียงพูดภาษาไทยแบบอัตโนมัติ รองรับการดึงข้อความจาก YouTube, Twitch และ TikTok พร้อมระบบแปลเป็นไทยก่อนอ่าน และ fallback ไปใช้ `gTTS` หาก `edge-tts` ใช้งานไม่ได้

## จุดเด่น

- รองรับ `YouTube Live`, `Twitch Chat`, และ `TikTok Live`
- มีทั้งโหมด `GUI` (`customtkinter`) และ `CLI`
- แปลข้อความต่างภาษาเป็นไทยอัตโนมัติด้วย `deep-translator`
- ใช้ `edge-tts` เป็นตัวหลัก และ fallback ไป `gTTS`
- มี queue แยกข้อความ/เสียง, duplicate filter และ auto-reconnect
- แยก log ตามแพลตฟอร์มไว้ในโฟลเดอร์ `logs/`

## สถานะโปรเจกต์ปัจจุบัน

entrypoints ที่ใช้กับ source code ในรีโปนี้ตอนนี้คือ:

- `start_gui.py`
- `start_cli.py`

ไฟล์อย่าง `run_gui.py`, `integration_test.py` และเอกสารบางส่วนใน `docs/` เป็นของเดิมจากโครงสร้างก่อนหน้าและไม่ควรใช้เป็นคู่มือหลักของเวอร์ชันปัจจุบัน

## การติดตั้ง

ต้องใช้ Python 3.10 ขึ้นไป และอินเทอร์เน็ตระหว่างใช้งาน

```bash
pip install -r requirements.txt
```

## การใช้งาน

### GUI

```bash
python start_gui.py
```

1. เปิดแพลตฟอร์มที่ต้องการผ่าน checkbox
2. กรอกค่า stream/channel/username
3. ตั้งค่าเสียง, delay, และ auto-translate
4. กด `START SYSTEM`

### CLI

แก้ค่าใน `config.ini` แล้วรัน:

```bash
python start_cli.py
```

ถ้าเปิด YouTube ไว้แต่ยังไม่ได้ใส่ `YOUTUBE_VIDEO_ID` ระบบจะถามค่าใน console

## ค่าคอนฟิกหลัก

คีย์สำคัญใน `config.ini`:

- `yt_enabled`, `YOUTUBE_VIDEO_ID`
- `tw_enabled`, `tw_channel`
- `tk_enabled`, `tk_username`
- `VOICE`
- `auto_translate`
- `delay_per_char`
- `max_delay`

หมายเหตุ: ใน `config.ini` หรือไฟล์เก่าอาจยังมีคีย์ `fb_*` ค้างอยู่ แต่ engine ปัจจุบันใน `core/` ไม่ได้ใช้งาน Facebook collector แล้ว

## โครงสร้างหลัก

```text
.
|-- start_gui.py
|-- start_cli.py
|-- core/
|   |-- tts_engine.py
|   |-- yt_chat.py
|   |-- twitch_chat.py
|   `-- tiktok_chat.py
|-- config.ini
|-- logs/
`-- docs/
```

## Log และการดีบัก

ระบบจะสร้าง log ไว้ใน `logs/` เช่น:

- `logs/log.txt`
- `logs/youtube.txt`
- `logs/twitch.txt`
- `logs/tiktok.txt`

ถ้ามีปัญหาเรื่องการเชื่อมต่อหรือเสียงไม่ออก ให้เริ่มตรวจจากไฟล์เหล่านี้ก่อน

## หมายเหตุ

- TikTok ใช้ไลบรารี `TikTokLive` ซึ่งอาจมีอาการ reconnect หรือ error จากภายในไลบรารีได้เป็นครั้งคราว
- Twitch ใช้วิธี anonymous IRC login จึงไม่ต้องใช้ API key
- ในรีโปมีไฟล์ build สำหรับ Windows อยู่แล้วใน `dist/` และ zip ที่ root สำหรับการแจกจ่าย
