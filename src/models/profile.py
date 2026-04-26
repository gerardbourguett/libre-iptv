from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

AVATAR_COLORS: list[str] = [
    "#00bcd4",  # cyan (default)
    "#4caf50",  # verde
    "#ff9800",  # naranja
    "#9c27b0",  # violeta
    "#f44336",  # rojo
    "#ffc107",  # amarillo
]


@dataclass
class HistoryEntry:
    channel_id: str
    watched_at: str = ""
    duration_s: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "channel_id": self.channel_id,
            "watched_at": self.watched_at,
            "duration_s": self.duration_s,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> HistoryEntry:
        return HistoryEntry(
            channel_id=str(data["channel_id"]),
            watched_at=str(data.get("watched_at", "")),
            duration_s=int(data.get("duration_s", 0)),
        )


@dataclass
class UserPrefs:
    theme: str = "midnight"
    accent_color: str = ""
    volume: int = 100
    subtitle_lang: str = ""
    last_channel: str = ""
    last_screen: str = "home"

    def to_dict(self) -> dict[str, Any]:
        return {
            "theme": self.theme,
            "accent_color": self.accent_color,
            "volume": self.volume,
            "subtitle_lang": self.subtitle_lang,
            "last_channel": self.last_channel,
            "last_screen": self.last_screen,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> UserPrefs:
        return UserPrefs(
            theme=str(data.get("theme", "midnight")),
            accent_color=str(data.get("accent_color", "")),
            volume=int(data.get("volume", 100)),
            subtitle_lang=str(data.get("subtitle_lang", "")),
            last_channel=str(data.get("last_channel", "")),
            last_screen=str(data.get("last_screen", "home")),
        )


@dataclass
class Profile:
    id: str
    name: str
    color: str
    playlist_url: str = ""
    playlist_path: str = ""
    favorites: list[str] = field(default_factory=list)
    recent: list[str] = field(default_factory=list)
    last_channel_url: str = ""
    pin_hash: str = ""
    blocked: dict[str, Any] = field(default_factory=dict)
    epg_url: str = ""
    history: list[HistoryEntry] = field(default_factory=list)
    prefs: UserPrefs = field(default_factory=UserPrefs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "playlist_url": self.playlist_url,
            "playlist_path": self.playlist_path,
            "favorites": list(self.favorites),
            "recent": list(self.recent),
            "last_channel_url": self.last_channel_url,
            "pin_hash": self.pin_hash,
            "blocked": dict(self.blocked),
            "epg_url": self.epg_url,
            "history": [h.to_dict() for h in self.history],
            "prefs": self.prefs.to_dict(),
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Profile:
        history_data = data.get("history", [])
        history = [HistoryEntry.from_dict(h) for h in history_data] if history_data else []
        prefs_data = data.get("prefs")
        prefs = UserPrefs.from_dict(prefs_data) if prefs_data else UserPrefs()
        return Profile(
            id=str(data["id"]),
            name=str(data["name"]),
            color=str(data["color"]),
            playlist_url=str(data.get("playlist_url", "")),
            playlist_path=str(data.get("playlist_path", "")),
            favorites=[str(v) for v in data.get("favorites", [])],
            recent=[str(v) for v in data.get("recent", [])],
            last_channel_url=str(data.get("last_channel_url", "")),
            pin_hash=str(data.get("pin_hash", "")),
            blocked=dict(data.get("blocked", {})),
            epg_url=str(data.get("epg_url", "")),
            history=history,
            prefs=prefs,
        )
