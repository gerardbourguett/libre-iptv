from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

from src.models.channel import Channel
from src.models.programme import EpgChannel, Programme


class ChannelCache:
    _TTL_SECONDS = 24 * 3600  # 24 hours

    def __init__(self, cache_dir: Path | None = None) -> None:
        if cache_dir is None:
            from src.platform import get_config_dir
            cache_dir = get_config_dir() / "cache"
        self._cache_dir = Path(cache_dir)
        self._channels_dir = self._cache_dir / "channels"
        self._channels_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, source_id: str) -> Path:
        return self._channels_dir / f"{source_id}.json"

    def get(self, source_id: str) -> list[Channel] | None:
        path = self._path(source_id)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            timestamp = float(data.get("timestamp", 0))
            if time.time() - timestamp > self._TTL_SECONDS:
                return None
            return [Channel(**item) for item in data.get("channels", [])]
        except Exception:
            return None

    def put(self, source_id: str, channels: list[Channel]) -> None:
        path = self._path(source_id)
        data = {
            "timestamp": time.time(),
            "channels": [ch.to_dict() for ch in channels],
        }
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(path)

    def invalidate(self, source_id: str) -> None:
        path = self._path(source_id)
        if path.exists():
            path.unlink()


class EpgCache:
    _TTL_SECONDS = 12 * 3600  # 12 hours

    def __init__(self, cache_dir: Path | None = None) -> None:
        if cache_dir is None:
            from src.platform import get_config_dir
            cache_dir = get_config_dir() / "cache"
        self._cache_dir = Path(cache_dir)
        self._epg_dir = self._cache_dir / "epg"
        self._epg_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, source_id: str) -> Path:
        return self._epg_dir / f"{source_id}.json"

    def get(self, source_id: str) -> tuple[list[EpgChannel], list[Programme]] | None:
        path = self._path(source_id)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            timestamp = float(data.get("timestamp", 0))
            if time.time() - timestamp > self._TTL_SECONDS:
                return None
            channels = [EpgChannel(**item) for item in data.get("channels", [])]
            programmes = [Programme(**item) for item in data.get("programmes", [])]
            return channels, programmes
        except Exception:
            return None

    def put(
        self,
        source_id: str,
        channels: list[EpgChannel],
        programmes: list[Programme],
    ) -> None:
        path = self._path(source_id)
        data = {
            "timestamp": time.time(),
            "channels": [ch.to_dict() for ch in channels],
            "programmes": [p.to_dict() for p in programmes],
        }
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(path)

    def invalidate(self, source_id: str) -> None:
        path = self._path(source_id)
        if path.exists():
            path.unlink()


class LogoCache:
    def __init__(self, cache_dir: Path | None = None) -> None:
        if cache_dir is None:
            from src.platform import get_config_dir
            cache_dir = get_config_dir() / "cache"
        self._cache_dir = Path(cache_dir)
        self._logos_dir = self._cache_dir / "logos"
        self._logos_dir.mkdir(parents=True, exist_ok=True)

    def _hash(self, url: str) -> str:
        return hashlib.sha256(url.encode()).hexdigest()[:16]

    def _path(self, url: str) -> Path:
        return self._logos_dir / f"{self._hash(url)}.png"

    def get(self, url: str) -> bytes | None:
        path = self._path(url)
        if not path.exists():
            return None
        try:
            return path.read_bytes()
        except Exception:
            return None

    def put(self, url: str, data: bytes) -> None:
        path = self._path(url)
        tmp = path.with_suffix(".png.tmp")
        tmp.write_bytes(data)
        tmp.replace(path)

    def invalidate(self, url: str) -> None:
        path = self._path(url)
        if path.exists():
            path.unlink()
