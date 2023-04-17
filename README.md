# EasyMLServe

## Setup

```
pip install -r requirements.txt
pip install -e .
```

Install ffmpeg for working with music files:

- [Install on windows for development. (Don't use the essential bundle, only the full)](https://phoenixnap.com/kb/ffmpeg-windows) or install with choco `choco install ffmpeg-full`
- [Download FFmpeg](https://ffmpeg.org/download.html)

## Run

- Start service

```
python3.9.exe .\genre_detection\service.py
```

- Start user interface

```
python3.9.exe .\genre_detection\ui.py
```
