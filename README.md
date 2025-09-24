# 🎬 YouTube Downloader (GUI, macOS/Windows/Linux)

A modern, lightweight desktop app to download YouTube videos or audio in just one click.  
Built with **Python + yt-dlp + CustomTkinter**, and bundled via **PyInstaller** for a native app experience.

---

## ✨ Features

- 📥 **Video & Audio download** (choose between MP4 video or MP3 audio)  
- ⚡ **Quality selection** (e.g. 1080p60, 720p, audio-only, etc.)  
- 📦 **Estimated file size** before you download  
- 🖼️ **Thumbnail & metadata preview** (title, channel, duration, description)  
- ⏳ **Progress bar** with live status  
- 📜 **Download history** with quick open-folder buttons  
- 🎨 **Light/Dark/System themes** (CustomTkinter styling)  
- ✅ **Ships with its own FFmpeg + FFprobe binaries** (no extra installs required)  

---

## 🚀 Getting Started

### Run from source

```
git clone https://github.com/yourusername/youtube-downloader.git
cd youtube-downloader

python3 -m venv .venv
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate      # Windows

pip install -r requirements.txt
python app.py
```
## To Build as an App
```
pyinstaller app.spec --noconfirm
```
Your native app will appear under the dist/ folder.

## 🛠️ Tech Stack

- Python 3.13+
- yt-dlp → YouTube extraction & downloads
- CustomTkinter → Modern themed Tkinter UI
- PIL (Pillow) → Image/thumbnail handling
- FFmpeg → Merging, conversion

## 📷 Screenshots
<img width="1764" height="1694" alt="image" src="https://github.com/user-attachments/assets/937126f6-50e2-4367-8346-c39e9c1e0ce5" />


## ⚖️ License
MIT License – free to use, modify, and share.
