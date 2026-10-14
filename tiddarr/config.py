"""Runtime configuration, read from environment variables.

Everything user-facing (library path, quality, schedules ...) lives in the
settings table and can be changed in the web UI. Environment variables only
cover what has to be known before the database exists.
"""

import os
from pathlib import Path

# Permissions of downloaded files and folders. Music libraries are usually
# shared with other apps (Jellyfin, SMB clients …), so default to open
# permissions; set e.g. TIDDARR_UMASK=022 for owner-only write access.
UMASK = int(os.environ.get("TIDDARR_UMASK", "000"), 8)
os.umask(UMASK)

DATA_DIR = Path(os.environ.get("TIDDARR_DATA_DIR", Path.home() / ".tiddarr"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

# tiddl keeps its auth token, config and API cache here. Point it at a
# directory inside DATA_DIR unless the user wants to share an existing one.
os.environ.setdefault("TIDDL_PATH", str(DATA_DIR / "tiddl"))
TIDDL_PATH = Path(os.environ["TIDDL_PATH"])
TIDDL_PATH.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "tiddarr.db"

HOST = os.environ.get("TIDDARR_HOST", "0.0.0.0")
PORT = int(os.environ.get("TIDDARR_PORT", "8688"))

# Optional HTTP basic auth for the web UI.
USERNAME = os.environ.get("TIDDARR_USERNAME", "")
PASSWORD = os.environ.get("TIDDARR_PASSWORD", "")

# Default for the library setting on first start.
DEFAULT_MUSIC_DIR = os.environ.get("TIDDARR_MUSIC_DIR", "/music")

# Command used to run tiddl; override if it is not on PATH.
TIDDL_BIN = os.environ.get("TIDDARR_TIDDL_BIN", "tiddl")

AUDIO_EXTENSIONS = {".flac", ".m4a", ".mp3", ".mp4", ".ogg", ".opus", ".wav", ".aac", ".alac"}

DEFAULT_SETTINGS = {
    "music_dir": DEFAULT_MUSIC_DIR,
    "quality": "max",
    "album_types": "ALBUM,EP,SINGLE",
    "monitor_new_default": "1",
    "refresh_hours": "12",
    "scan_hours": "6",
    "threads": "4",
    "embed_artwork": "1",
    "folder_artwork": "1",
    "chart_countries": "world,at,de",
    "chart_types": "song,album,artist",
    "chart_size": "50",
    "jellyfin_url": "",  # legacy, moved to the integrations settings
    "jellyfin_api_key": "",
}
