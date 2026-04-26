from __future__ import annotations

import hashlib
from collections import OrderedDict
from pathlib import Path
from typing import TYPE_CHECKING, cast

from PyQt6.QtCore import QObject, QTimer, QUrl, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QWidget


class _FailedSentinel:
    pass


class LogoCache:
    """LRU cache for QPixmap objects keyed by logo URL."""

    def __init__(self, maxsize: int = 200) -> None:
        self._maxsize = maxsize
        self._data: OrderedDict[str, QPixmap] = OrderedDict()

    def get(self, url: str) -> QPixmap | None:
        if url not in self._data:
            return None
        self._data.move_to_end(url)
        return self._data[url]

    def put(self, url: str, pixmap: QPixmap) -> None:
        if url in self._data:
            self._data.move_to_end(url)
            self._data[url] = pixmap
            return
        if len(self._data) >= self._maxsize:
            self._data.popitem(last=False)
        self._data[url] = pixmap

    def __contains__(self, url: str) -> bool:
        return url in self._data


class LogoLoader(QObject):
    logo_loaded = pyqtSignal(str)  # emits URL when logo ready (or failed)
    _FAILED: QPixmap = cast(QPixmap, _FailedSentinel())

    def __init__(
        self,
        parent: QWidget | None = None,
        timeout_ms: int = 5000,
        cache_dir: Path | None = None,
    ) -> None:
        super().__init__(parent)
        self._cache = LogoCache(maxsize=200)
        self._in_flight: set[str] = set()
        self._nam = QNetworkAccessManager(self)
        self._timeout_ms = timeout_ms
        self._timeout_timers: dict[str, QTimer] = {}
        self._cache_dir: Path | None = None
        self._logos_dir: Path | None = None
        if cache_dir is not None:
            self._cache_dir = Path(cache_dir)
            self._logos_dir = self._cache_dir / "logos"
            self._logos_dir.mkdir(parents=True, exist_ok=True)

    def _disk_hash(self, url: str) -> str:
        return hashlib.sha256(url.encode()).hexdigest()[:16]

    def _disk_path(self, url: str) -> Path | None:
        if self._logos_dir is None:
            return None
        return self._logos_dir / f"{self._disk_hash(url)}.png"

    def _load_from_disk(self, url: str) -> QPixmap | None:
        path = self._disk_path(url)
        if path is None or not path.exists():
            return None
        pixmap = QPixmap()
        if pixmap.load(str(path)):
            return pixmap
        return None

    def _save_to_disk(self, url: str, data: bytes) -> None:
        path = self._disk_path(url)
        if path is None:
            return
        tmp = path.with_suffix(".png.tmp")
        tmp.write_bytes(data)
        tmp.replace(path)

    def invalidate(self, url: str) -> None:
        path = self._disk_path(url)
        if path is not None and path.exists():
            path.unlink()
        if url in self._cache:
            del self._cache._data[url]

    def request(self, url: str) -> None:
        if url in self._cache:
            self.logo_loaded.emit(url)
            return

        # Try disk cache before network
        disk_pixmap = self._load_from_disk(url)
        if disk_pixmap is not None:
            self._cache.put(url, disk_pixmap)
            self.logo_loaded.emit(url)
            return

        if url in self._in_flight:
            return

        self._in_flight.add(url)
        req = QNetworkRequest(QUrl(url))
        reply = self._nam.get(req)
        if reply is None:
            self._in_flight.discard(url)
            return

        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda u=url, r=reply: self._on_timeout(u, r))
        timer.start(self._timeout_ms)
        self._timeout_timers[url] = timer

        reply.finished.connect(lambda r=reply, u=url: self._on_reply_finished(r, u))

    def _on_timeout(self, url: str, reply: QNetworkReply) -> None:
        if url in self._in_flight:
            self._in_flight.discard(url)
            self._cache.put(url, LogoLoader._FAILED)
            reply.abort()
            self.logo_loaded.emit(url)
        self._timeout_timers.pop(url, None)

    def _on_reply_finished(self, reply: QNetworkReply, url: str) -> None:
        self._timeout_timers.pop(url, None)
        if url not in self._in_flight:
            return
        self._in_flight.discard(url)

        if reply.error() != QNetworkReply.NetworkError.NoError:
            self._cache.put(url, LogoLoader._FAILED)
        else:
            data = reply.readAll()
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            if pixmap.isNull():
                self._cache.put(url, LogoLoader._FAILED)
            else:
                self._cache.put(url, pixmap)
                self._save_to_disk(url, data)

        self.logo_loaded.emit(url)

    def get_pixmap(self, url: str) -> QPixmap | None:
        if url in self._cache:
            result = self._cache.get(url)
            if result is LogoLoader._FAILED:
                return LogoLoader._FAILED
            return result
        if url in self._in_flight:
            return None
        return None
