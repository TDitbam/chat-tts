# Migration note: stable entrypoint

- Old files are kept as requested (`main.py`, `main1.py`, `blackup.py`).
- New recommended entrypoint is `main_v2.py`.

## Run
```bash
python main_v2.py
```

## Key fixes in v2
- Added safer delay validation and normalization.
- Improved YouTube video-id extraction (`watch`, `youtu.be`, `live`, `shorts`, `embed`).
- Added global pruning for spam-tracking memory growth.
- Fixed blacklist add flow to consistently use lowercase.
- Added explicit dependency support for `playsound3` in `requirements.txt`.
