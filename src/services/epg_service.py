from __future__ import annotations

import bisect
import hashlib
import json
import os
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from src.models.programme import EpgChannel, Programme
from src.parser.xmltv import XmltvParseError, parse_xmltv_url


class EpgFetchWorker(QThread):
    finished = pyqtSignal(list, list)
    error = pyqtSignal(str)

    def __init__(self, url: str) -> None:
        super().__init__()
        self._url = url

    def run(self) -> None:
        try:
            channels, programmes = parse_xmltv_url(self._url)
            self.finished.emit(channels, programmes)
        except Exception as exc:
            self.error.emit(str(exc))


class EpgService(QObject):
    epg_ready = pyqtSignal()
    epg_error = pyqtSignal(str)

    def __init__(
        self,
        cache_dir: Path | None = None,
        refresh_hours: int = 24,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        if cache_dir is None:
            from src.platform import get_config_dir
            cache_dir = get_config_dir() / "epg_cache"
        self._cache_dir = cache_dir
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._refresh_hours = refresh_hours
        self._worker: EpgFetchWorker | None = None
        self._programmes: dict[str, list[Programme]] = {}
        self._channels: list[EpgChannel] = []
        self._last_url: str = ""

    def start(self, url: str) -> None:
        if not url:
            self._programmes = {}
            self._channels = []
            self._last_url = ""
            self.epg_ready.emit()
            return

        self._last_url = url
        cached = self._load_cache(url)
        if cached is not None:
            self._channels, self._programmes = cached
            self.epg_ready.emit()
            return

        self._worker = EpgFetchWorker(url)
        self._worker.finished.connect(self._on_fetch_finished)
        self._worker.error.connect(self._on_fetch_error)
        self._worker.start()

    def stop(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            self._worker.quit()
            self._worker.wait(5000)
        self._worker = None

    def get_now_next(self, tvg_id: str) -> tuple[Programme | None, Programme | None]:
        progs = self._programmes.get(tvg_id, [])
        if not progs:
            return None, None

        now_str = time.strftime("%Y%m%d%H%M%S %z", time.gmtime())
        starts = [p.start for p in progs]
        idx = bisect.bisect_right(starts, now_str) - 1
        if idx < 0:
            return None, progs[0] if progs else None
        now_prog = progs[idx]
        next_prog = progs[idx + 1] if idx + 1 < len(progs) else None
        return now_prog, next_prog

    def _cache_file(self, url: str) -> Path:
        key = hashlib.sha256(url.encode("utf-8")).hexdigest()
        return self._cache_dir / f"{key}.json"

    def _load_cache(
        self, url: str
    ) -> tuple[list[EpgChannel], dict[str, list[Programme]]] | None:
        cache_file = self._cache_file(url)
        if not cache_file.exists():
            return None
        mtime = cache_file.stat().st_mtime
        age_hours = (time.time() - mtime) / 3600
        if age_hours >= self._refresh_hours:
            return None
        try:
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            if data.get("url") != url:
                return None
            channels = [EpgChannel(**c) for c in data.get("channels", [])]
            programmes = [Programme.from_dict(p) for p in data.get("programmes", [])]
            programmes_by_channel: dict[str, list[Programme]] = {}
            for p in programmes:
                programmes_by_channel.setdefault(p.channel, []).append(p)
            for ch_progs in programmes_by_channel.values():
                ch_progs.sort(key=lambda pr: pr.start)
            return channels, programmes_by_channel
        except Exception:
            return None

    def _save_cache(
        self, url: str, channels: list[EpgChannel], programmes: list[Programme]
    ) -> None:
        cache_file = self._cache_file(url)
        data: dict[str, Any] = {
            "url": url,
            "channels": [{"id": c.id, "names": c.names, "icon": c.icon} for c in channels],
            "programmes": [p.to_dict() for p in programmes],
        }
        cache_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _on_fetch_finished(self, channels: list[EpgChannel], programmes: list[Programme]) -> None:
        self._channels = channels
        self._programmes = {}
        for p in programmes:
            self._programmes.setdefault(p.channel, []).append(p)
        for ch_progs in self._programmes.values():
            ch_progs.sort(key=lambda pr: pr.start)
        if self._last_url:
            self._save_cache(self._last_url, channels, programmes)
        self.epg_ready.emit()
        self._worker = None

    def _on_fetch_error(self, message: str) -> None:
        self.epg_error.emit(message)
        self._worker = None

    def _fetch_and_parse(self, url: str) -> tuple[list[EpgChannel], list[Programme]]:
        """Synchronous fetch for testing."""
        return parse_xmltv_url(url)
