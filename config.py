import os, json
from datetime import datetime

APP_DIR  = os.path.join(os.path.expanduser("~"), ".yt_downloader_gui")
CFG_PATH = os.path.join(APP_DIR, "config.json")

DEFAULTS = {
    "theme": "light",
    "default_folder": os.path.join(os.path.expanduser("~"), "Downloads"),
    "default_mode": "video",
    "default_template": "%(title)s.%(ext)s",
    "history": []
}

def ensure_app_dir():
    os.makedirs(APP_DIR, exist_ok=True)

def save_config(cfg):
    ensure_app_dir()
    with open(CFG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

def load_config():
    ensure_app_dir()
    if not os.path.exists(CFG_PATH):
        save_config(DEFAULTS.copy())
        return DEFAULTS.copy()
    try:
        with open(CFG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception:
        cfg = DEFAULTS.copy()
    for k, v in DEFAULTS.items():
        cfg.setdefault(k, v)
    return cfg

def add_history_entry(cfg, title, url, mode, path, thumb=None):
    cfg["history"].append({
        "title": title or "",
        "url": url,
        "mode": mode,
        "path": path or "",
        "time": datetime.now().isoformat(timespec="seconds"),
        "thumb": thumb or ""
    })
    cfg["history"] = cfg["history"][-100:]
    save_config(cfg)

def clear_history(cfg):
    cfg["history"] = []
    save_config(cfg)
