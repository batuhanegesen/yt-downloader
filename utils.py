import shutil, platform, subprocess, os
from PIL import Image, ImageDraw

def ffmpeg_available():
    return shutil.which("ffmpeg") is not None

def add_rounded_corners(img, radius=16):
    img = img.convert("RGBA")
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w, h], radius, fill=255)
    rounded = Image.new("RGBA", (w, h))
    rounded.paste(img, (0, 0), mask=mask)
    return rounded

def open_in_folder(path):
    if not path: return
    folder = os.path.dirname(path) or path
    sys = platform.system()
    if sys == "Darwin":
        subprocess.call(["open", "-R", path]) if os.path.exists(path) else subprocess.call(["open", folder])
    elif sys == "Windows":
        subprocess.call(["explorer", "/select,", path]) if os.path.exists(path) else subprocess.call(["explorer", folder])
    else:
        subprocess.call(["xdg-open", folder])

def notify(title, message):
    sys = platform.system()
    if sys == "Darwin":  # macOS
        subprocess.call(["osascript", "-e",
                        f'display notification "{message}" with title "{title}"'])
    elif sys == "Linux":
        subprocess.call(["notify-send", title, message])
    elif sys == "Windows":
        try:
            from win10toast import ToastNotifier
            ToastNotifier().show_toast(title, message, duration=5)
        except:
            pass
