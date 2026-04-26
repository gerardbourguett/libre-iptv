from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EpgChannel:
    id: str
    names: list[str]
    icon: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "names": list(self.names),
            "icon": self.icon,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> EpgChannel:
        return EpgChannel(
            id=str(data["id"]),
            names=[str(v) for v in data.get("names", [])],
            icon=str(data.get("icon", "")),
        )


@dataclass(frozen=True)
class Programme:
    channel: str
    title: str
    start: str
    stop: str
    description: str = ""
    category: str = ""
    icon: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "channel": self.channel,
            "title": self.title,
            "start": self.start,
            "stop": self.stop,
            "description": self.description,
            "category": self.category,
            "icon": self.icon,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Programme:
        return Programme(
            channel=str(data["channel"]),
            title=str(data["title"]),
            start=str(data["start"]),
            stop=str(data["stop"]),
            description=str(data.get("description", "")),
            category=str(data.get("category", "")),
            icon=str(data.get("icon", "")),
        )
