from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any


def _generate_id(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:12]


@dataclass(frozen=True)
class Channel:
    url: str
    name: str
    tvg_id: str = field(default="")
    tvg_name: str = field(default="")
    tvg_logo: str = field(default="")
    group: str = field(default="")
    # NEW — all with defaults for backward compat
    id: str = field(default="")
    num: int = field(default=0)
    is_live: bool = field(default=True)
    is_vod: bool = field(default=False)
    is_series: bool = field(default=False)

    def __post_init__(self) -> None:
        if not self.id:
            object.__setattr__(self, "id", _generate_id(self.url))

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "name": self.name,
            "tvg_id": self.tvg_id,
            "tvg_name": self.tvg_name,
            "tvg_logo": self.tvg_logo,
            "group": self.group,
            "id": self.id,
            "num": self.num,
            "is_live": self.is_live,
            "is_vod": self.is_vod,
            "is_series": self.is_series,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Channel:
        return Channel(
            url=str(data["url"]),
            name=str(data["name"]),
            tvg_id=str(data.get("tvg_id", "")),
            tvg_name=str(data.get("tvg_name", "")),
            tvg_logo=str(data.get("tvg_logo", "")),
            group=str(data.get("group", "")),
            id=str(data.get("id", "")),
            num=int(data.get("num", 0)),
            is_live=bool(data.get("is_live", True)),
            is_vod=bool(data.get("is_vod", False)),
            is_series=bool(data.get("is_series", False)),
        )
