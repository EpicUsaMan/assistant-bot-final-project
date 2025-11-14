from __future__ import annotations
import os
import sys
from pathlib import Path

APP_NAME = "assistant-bot"
DEFAULT_FILE = "addressbook.pkl"

def get_user_data_dir(app_name: str = APP_NAME) -> Path:
    home = Path.home()

    # macOS
    if sys.platform == "darwin":
        base = home / "Library" / "Application Support" / app_name
    # Windows
    elif sys.platform == "nt":
        base = Path(os.getenv("APPDATA", home / "AppData" / "Roaming")) / app_name # fallback to ~/AppData/Roaming
    # Linux or other
    else:
        base = home / f".{app_name}"
    base.mkdir(parents=True, exist_ok=True)

    return base

def get_storage_path(filename: str = DEFAULT_FILE) -> Path:
    return get_user_data_dir() / filename