from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class SourceType(Enum):
    M3U_URL = "m3u_url"
    M3U_FILE = "m3u_file"
    XTREAM = "xtream"


@dataclass
class Source:
    id: str
    name: str
    type: SourceType
    enabled: bool = True
    last_updated: str = ""
    auto_refresh: bool = False
    refresh_interval: int = 60
    url: str = ""
    path: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["type"] = self.type.value
        return d

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Source:
        return Source(
            id=str(data["id"]),
            name=str(data["name"]),
            type=SourceType(data["type"]),
            enabled=bool(data.get("enabled", True)),
            last_updated=str(data.get("last_updated", "")),
            auto_refresh=bool(data.get("auto_refresh", False)),
            refresh_interval=int(data.get("refresh_interval", 60)),
            url=str(data.get("url", "")),
            path=str(data.get("path", "")),
        )


class SourceManager:
    def __init__(self, config_dir: Path | None = None) -> None:
        if config_dir is None:
            from src.platform import get_config_dir
            config_dir = get_config_dir()
        self._config_dir = Path(config_dir)
        self._sources: dict[str, Source] = {}
        self._load()

    @property
    def _sources_path(self) -> Path:
        return self._config_dir / "sources.json"

    def _load(self) -> None:
        if not self._sources_path.exists():
            return
        try:
            raw = json.loads(self._sources_path.read_text(encoding="utf-8"))
            for item in raw:
                try:
                    src = Source.from_dict(item)
                    self._sources[src.id] = src
                except Exception:
                    continue
        except Exception:
            self._sources = {}

    def _save(self) -> None:
        data = [s.to_dict() for s in self._sources.values()]
        tmp = self._sources_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(self._sources_path)

    def add_source(
        self,
        name: str,
        type_: SourceType,
        *,
        url: str = "",
        path: str = "",
    ) -> Source:
        source = Source(
            id=str(uuid.uuid4()),
            name=name,
            type=type_,
            url=url,
            path=path,
        )
        self._sources[source.id] = source
        self._save()
        return source

    def list_sources(self) -> list[Source]:
        return list(self._sources.values())

    def get_source(self, source_id: str) -> Source | None:
        return self._sources.get(source_id)

    def enable(self, source_id: str) -> None:
        src = self._sources.get(source_id)
        if src is not None:
            src.enabled = True
            self._save()

    def disable(self, source_id: str) -> None:
        src = self._sources.get(source_id)
        if src is not None:
            src.enabled = False
            self._save()

    def delete(self, source_id: str) -> None:
        if source_id in self._sources:
            del self._sources[source_id]
            self._save()
