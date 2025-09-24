# downloader.py
import yt_dlp
import threading
from io import BytesIO
import requests
import os
import sys

# Detect ffmpeg path depending on build state
if getattr(sys, 'frozen', False):
    ffmpeg_path = os.path.join(sys._MEIPASS, "ffmpeg", "ffmpeg")
else:
    ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg-bin", "ffmpeg")

video_size_map = {}     # label → filesize
video_format_map = {}   # label → yt-dlp format_id
video_is_videoonly = {} # label → True/False


def fetch_metadata(url, on_done, on_error, set_step=None):
    """Fetch metadata and available formats for a given URL."""
    def task():
        try:
            if set_step:
                set_step("📡 Fetching metadata…", 0)
            ydl_opts = {"quiet": True, "skip_download": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get("formats", [])

                video_size_map.clear()
                video_format_map.clear()
                video_is_videoonly.clear()

                choices = []
                for f in formats:
                    if f.get("vcodec") != "none":  # video
                        height = f.get("height")
                        ext = f.get("ext")
                        fmt_id = f.get("format_id")
                        label = f"{height}p - {ext}"

                        if f.get("filesize"):
                            video_size_map[label] = f["filesize"]
                        video_format_map[label] = fmt_id
                        video_is_videoonly[label] = (f.get("acodec") == "none")
                        choices.append(label)

                choices = sorted(set(choices))

                # thumbnail
                thumb_data = None
                if info.get("thumbnail"):
                    try:
                        resp = requests.get(info["thumbnail"], timeout=5)
                        thumb_data = BytesIO(resp.content)
                    except:
                        pass

                if on_done:
                    on_done(info, choices, thumb_data)
        except Exception as e:
            if on_error:
                on_error(str(e))

    threading.Thread(target=task, daemon=True).start()


def download(cfg, url, folder, mode, quality, template, ui_hooks):
    """Download video or audio with yt-dlp."""
    def task():
        try:
            def progress_hook(d):
                if d["status"] == "downloading":
                    total = d.get("total_bytes") or d.get("total_bytes_estimate")
                    percent = d.get("downloaded_bytes", 0) / total if total else 0
                    ui_hooks["set_step"](f"⬇️ Downloading… {d.get('_percent_str','')}", percent)
                elif d["status"] == "finished":
                    ui_hooks["set_step"]("✅ Download complete", 1.0)

            if mode == "audio":
                fmt = "bestaudio/best"
                postprocessors = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }]
            else:  # video
                fmt_id = video_format_map.get(quality)
                if not fmt_id:
                    fmt = "bestvideo+bestaudio/best"
                else:
                    if video_is_videoonly.get(quality, False):
                        # sadece video stream → bestaudio ile birleştir
                        fmt = f"{fmt_id}+bestaudio"
                    else:
                        # birleşik stream
                        fmt = fmt_id
                postprocessors = []

            ydl_opts = {
                "format": fmt,
                "progress_hooks": [progress_hook],
                "outtmpl": os.path.join(folder, template),
                "quiet": True,
                "noprogress": False,
                "continuedl": False,
                "nopart": True,
                "http_chunk_size": None,
                "postprocessors": postprocessors,
                "ffmpeg_location": ffmpeg_path,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            if ui_hooks.get("on_done"):
                ui_hooks["on_done"]()

        except Exception as e:
            if ui_hooks.get("on_error"):
                ui_hooks["on_error"](str(e))

    threading.Thread(target=task, daemon=True).start()
