# app-mac.spec

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[('./ffmpeg-macos', 'ffmpeg')],
    datas=[
        ('config.py', '.'),
        ('downloader.py', '.'),
        ('utils.py', '.'),
    ],
    hiddenimports=['PIL._tkinter_finder'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='YoutubeDownloader',
    console=True,   # keep console for debugging for now
)

app = BUNDLE(
    exe,
    name='YoutubeDownloader.app',
    icon=None,
    bundle_identifier='com.batu.youtubedownloader',
)
