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
class Profile:
    id: str
    name: str
    color: str
    playlist_url: str = ""
    playlist_path: str = ""
    favorites: list[str] = field(default_factory=list)
    recent: list[str] = field(default_factory=list)
    last_channel_url: str = ""

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
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Profile:
        return Profile(
            id=str(data["id"]),
            name=str(data["name"]),
            color=str(data["color"]),
            playlist_url=str(data.get("playlist_url", "")),
            playlist_path=str(data.get("playlist_path", "")),
            favorites=[str(v) for v in data.get("favorites", [])],
            recent=[str(v) for v in data.get("recent", [])],
            last_channel_url=str(data.get("last_channel_url", "")),
        )
