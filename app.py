import customtkinter as ctk
from tkinter import filedialog
from config import load_config, save_config
from downloader import fetch_metadata, download, video_size_map
from utils import open_in_folder

import os
from PIL import Image
import requests
from io import BytesIO

cfg = load_config()
ctk.set_appearance_mode(cfg["theme"])
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("YouTube Downloader")
app.geometry("880x900")

# ------------------- Helpers -------------------
def set_step(name, percent=0.0):
    def update():
        status_label.configure(text=name)
        progress_bar.set(percent)
        app.update_idletasks()   # forces redraw
    app.after(0, update)

# ------------------- Downloader Tab -------------------
def on_url_change(*_):
    urls = url_var.get().strip().splitlines()
    if not urls: return
    first_url = urls[0]
    set_step("📡 Fetching metadata…", 0)
    fetch_metadata(first_url, on_metadata_done, on_metadata_error, set_step=set_step)

def on_metadata_done(info, choices, thumb_data):
    title = info.get("title", "Unknown Title")
    channel = info.get("uploader", "Unknown Channel")
    duration = info.get("duration_string") or str(info.get("duration"))
    desc = (info.get("description") or "")
    if len(desc) > 240: desc = desc[:240] + "..."

    meta = f"📺 {title}\n👤 {channel}\n⏱ {duration}\n\n{desc}"
    metadata_label.configure(text=meta)

    if thumb_data:
        img = Image.open(thumb_data).resize((220, 124))
        img = img.convert("RGBA")
        tkimg = ctk.CTkImage(light_image=img, dark_image=img, size=(220, 124))
        thumbnail_label.configure(image=tkimg, text="")
        thumbnail_label.image = tkimg

    if choices:
        quality_menu.configure(values=choices)
        quality_var.set(choices[-1])
        update_size_label(choices[-1])

    set_step("✅ Metadata loaded", 1.0)

def on_metadata_error(msg):
    set_step(f"❌ {msg}", 1.0)

def update_size_label(choice):
    size = video_size_map.get(choice)
    if size:
        size_mb = round(size/(1024*1024), 1)
        size_label.configure(text=f"📦 Estimated size: {size_mb} MB")
    else:
        size_label.configure(text="📦 Estimated size: Unknown")

def start_download():
    urls = url_var.get().strip().splitlines()
    if not urls:
        status_label.configure(text="❌ Enter at least one URL")
        return

    folder = folder_var.get()
    mode   = mode_var.get()
    template = template_var.get()
    quality = quality_var.get()

    progress_bar.set(0)
    status_label.configure(text="Preparing download…")

    ui_hooks = {
        "set_step": set_step,
        "on_done": lambda: app.after(0, lambda: status_label.configure(text="✅ All steps done")),
        "on_error": lambda msg: app.after(0, lambda: status_label.configure(text=f"❌ {msg}"))
    }

    for url in urls:
        download(cfg, url.strip(), folder, mode, quality, template, ui_hooks)

# ------------------- UI -------------------
tabs = ctk.CTkTabview(app, width=820, height=820, corner_radius=16)
tabs.pack(expand=True, fill="both", padx=16, pady=16)
downloader_tab = tabs.add("⬇️ Downloader")
history_tab    = tabs.add("📜 History")
settings_tab   = tabs.add("⚙️ Settings")

# Downloader tab
dl_main = ctk.CTkFrame(downloader_tab)
dl_main.pack(fill="both", expand=True, padx=10, pady=10)

url_var = ctk.StringVar()
url_var.trace_add("write", on_url_change)
ctk.CTkLabel(dl_main, text="🔗 Paste YouTube URL(s):").pack(anchor="w", padx=10, pady=(10,0))
url_entry = ctk.CTkTextbox(dl_main, height=70)
url_entry.pack(padx=10, pady=5, fill="x")
url_entry.configure(font=("Arial", 12))
url_entry.bind("<<Modified>>", lambda e: url_var.set(url_entry.get("1.0", "end-1c")))

info_frame = ctk.CTkFrame(dl_main, corner_radius=12)
info_frame.pack(padx=10, pady=10, fill="x")
thumbnail_label = ctk.CTkLabel(info_frame, text="", width=220, height=124)
thumbnail_label.pack(side="left", padx=10, pady=10)
metadata_label = ctk.CTkLabel(info_frame, text="", justify="left", wraplength=500)
metadata_label.pack(side="left", padx=10, pady=10, fill="x", expand=True)

opts_frame = ctk.CTkFrame(dl_main, corner_radius=12)
opts_frame.pack(padx=10, pady=10, fill="x")

folder_var = ctk.StringVar(value=cfg["default_folder"])
ctk.CTkLabel(opts_frame, text="📂 Save to:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
ctk.CTkEntry(opts_frame, textvariable=folder_var).grid(row=0, column=1, padx=10, pady=5, sticky="ew")
ctk.CTkButton(opts_frame, text="Browse", command=lambda: folder_var.set(filedialog.askdirectory() or folder_var.get())).grid(row=0, column=2, padx=10, pady=5)

mode_var = ctk.StringVar(value=cfg["default_mode"])
ctk.CTkRadioButton(opts_frame, text="Video", variable=mode_var, value="video").grid(row=1, column=0, padx=10, pady=5)
ctk.CTkRadioButton(opts_frame, text="Audio (MP3)", variable=mode_var, value="audio").grid(row=1, column=1, padx=10, pady=5)

ctk.CTkLabel(opts_frame, text="Quality:").grid(row=2, column=0, padx=10, pady=5)
quality_var = ctk.StringVar(value="best")
quality_menu = ctk.CTkOptionMenu(opts_frame, variable=quality_var, values=["best"], command=update_size_label)
quality_menu.grid(row=2, column=1, padx=10, pady=5)

template_var = ctk.StringVar(value=cfg.get("default_template", "%(title)s.%(ext)s"))
ctk.CTkLabel(opts_frame, text="Filename template:").grid(row=3, column=0, padx=10, pady=5)
ctk.CTkOptionMenu(opts_frame, variable=template_var,
                  values=["%(title)s.%(ext)s", "%(uploader)s - %(title)s.%(ext)s"]).grid(row=3, column=1, padx=10, pady=5)

opts_frame.grid_columnconfigure(1, weight=1)

ctk.CTkButton(dl_main, text="⬇️ Download", command=start_download, height=40).pack(padx=10, pady=15, fill="x")

progress_bar = ctk.CTkProgressBar(dl_main)
progress_bar.pack(padx=10, pady=5, fill="x")
progress_bar.set(0)
status_label = ctk.CTkLabel(dl_main, text="")
status_label.pack(pady=5)
size_label = ctk.CTkLabel(dl_main, text="")
size_label.pack()

# ------------------- History Tab -------------------
def refresh_history_list():
    for child in hist_frame.winfo_children(): child.destroy()
    for item in reversed(cfg.get("history", [])):
        row = ctk.CTkFrame(hist_frame, corner_radius=8)
        row.pack(fill="x", padx=10, pady=5)
        if item.get("thumb"):
            try:
                resp = requests.get(item["thumb"], timeout=5)
                img = Image.open(BytesIO(resp.content)).resize((80,45))
                tkimg = ctk.CTkImage(light_image=img, dark_image=img, size=(80,45))
                thumb = ctk.CTkLabel(row, image=tkimg, text="")
                thumb.image = tkimg
                thumb.pack(side="left", padx=5)
            except: pass
        text = f"{item['title']} ({item['mode'].upper()})\n{item['time']}"
        ctk.CTkLabel(row, text=text, justify="left").pack(side="left", padx=10)
        ctk.CTkButton(row, text="Open", width=80,
                      command=lambda p=item["path"]: open_in_folder(p)).pack(side="right", padx=5)

hist_frame = ctk.CTkScrollableFrame(history_tab)
hist_frame.pack(fill="both", expand=True, padx=10, pady=10)
refresh_history_list()

# ------------------- Settings Tab -------------------
def apply_theme(name):
    ctk.set_appearance_mode(name)
    cfg["theme"] = name
    save_config(cfg)

def apply_defaults():
    cfg["default_folder"] = folder_var.get()
    cfg["default_mode"]   = mode_var.get()
    cfg["default_template"] = template_var.get()
    save_config(cfg)

ctk.CTkLabel(settings_tab, text="Preferences", font=("Arial",16,"bold")).pack(anchor="w", padx=10, pady=10)
theme_var = ctk.StringVar(value=cfg["theme"])
ctk.CTkOptionMenu(settings_tab, variable=theme_var, values=["light","dark","system"], command=apply_theme).pack(padx=10, pady=5)
ctk.CTkButton(settings_tab, text="Save Defaults", command=apply_defaults).pack(padx=10, pady=10)

tabs.set("⬇️ Downloader")
app.mainloop()
