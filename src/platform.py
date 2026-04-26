from __future__ import annotations

import logging
import shutil
import sys
from pathlib import Path
from typing import Any

import vlc
from platformdirs import user_config_dir

APP_NAME = "iptv-player"


def get_config_dir() -> Path:
    """Return OS-appropriate config dir, creating it if needed."""
    path = Path(user_config_dir(APP_NAME))
    path.mkdir(parents=True, exist_ok=True)
    return path


def bind_vlc(media_player: Any, win_id: int) -> None:
    """Dispatch VLC binding by sys.platform. Raises RuntimeError on unknown OS."""
    if sys.platform == "win32":
        media_player.set_hwnd(win_id)
    elif sys.platform == "darwin":
        media_player.set_nsobject(win_id)
    elif sys.platform == "linux":
        media_player.set_xid(win_id)
    else:
        raise RuntimeError(f"Unsupported platform: {sys.platform}")


def check_vlc() -> None:
    """Try import vlc + vlc.Instance(). Raise ImportError with install instructions."""
    try:
        vlc.Instance()
    except Exception as exc:
        install_cmd = _get_vlc_install_cmd()
        msg = (
            f"VLC is required but not found.\n"
            f"Download: https://www.videolan.org/\n"
            f"Install command: {install_cmd}"
        )
        raise ImportError(msg) from exc


def _get_vlc_install_cmd() -> str:
    if sys.platform == "win32":
        return "choco install vlc"
    if sys.platform == "darwin":
        return "brew install --cask vlc"
    return "sudo apt install vlc"


def migrate_from_legacy() -> None:
    """Copy legacy profiles on Windows when the new platform dir is missing."""
    if sys.platform != "win32":
        return
    legacy = Path.home() / ".config" / APP_NAME / "profiles"
    if not legacy.exists():
        return
    new_dir = get_config_dir() / "profiles"
    if new_dir.exists():
        return
    shutil.copytree(legacy, new_dir)
    logging.warning(
        "Migrated profile data from legacy path: %s -> %s", legacy, new_dir
    )


def get_platform_font() -> str:
    """Return the platform font name (Segoe UI, SF Display, or system default)."""
    if sys.platform == "win32":
        return "Segoe UI"
    if sys.platform == "darwin":
        return "SF Display"
    return ""
