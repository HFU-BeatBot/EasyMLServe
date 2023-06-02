# EasyMLServe

## Use the website

<details>
<summary>Click here when you are interested in how to use the website.</summary>

![How To Use Website](assets/how_to_website.png)

</details>

## Local Development (on Windows PC)

### Install packages

```
pip install -r requirements.txt
pip install -e .
```

Install ffmpeg for working with music files:

- [Install on windows for development. (Don't use the essential bundle, only the full)](https://phoenixnap.com/kb/ffmpeg-windows) or install with choco `choco install ffmpeg-full`
- [Download FFmpeg](https://ffmpeg.org/download.html)

### Run

- Start service

```
python3.9.exe .\genre_detection\service.py
```

- Start user interface

```
python3.9.exe .\genre_detection\ui.py
```

## Setup Ubuntu VM

- Clone from Git repository
- Create virtual environment

```
sudo apt install python3-virtualenv
virtualenv --python python3 venv
```

- Activate venv

```
source venv/bin/activate
```

- Install packages

```
pip install -r requirements.txt
```

- Install missing packages on VM

```
sudo apt install libglu1-mesa

sudo apt install libxkbcommon-x11-0

sudo apt install libgl1

sudo apt install libegl1-mesa

sudo apt install ffmpeg
```

### Run

- Start service

```
python genre_detection/service.py
```

- Start user interface

```
python genre_detection/ui.py
```

## Related project

Here's the original project where the code was coming from. We adapted a few things to match our needs.

- [EasyMLServe](https://github.com/KIT-IAI/EasyMLServe/)

## License

This code is licensed under the [MIT License](https://github.com/KIT-IAI/EasyMLServe/blob/main/LICENSE).
