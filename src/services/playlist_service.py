from __future__ import annotations

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from src.i18n import t
from src.models.channel import Channel
from src.models.profile import Profile
from src.parser.m3u import fetch_best_playlist, parse_m3u_file


class PlaylistFetchWorker(QThread):
    fetched: pyqtSignal = pyqtSignal(list)
    error: pyqtSignal = pyqtSignal(str)

    def __init__(self, url: str) -> None:
        super().__init__()
        self._url = url

    def run(self) -> None:
        try:
            channels = fetch_best_playlist(self._url)
            self.fetched.emit(channels)
        except Exception as e:
            self.error.emit(str(e))


class PlaylistService(QObject):
    channels_loaded = pyqtSignal(list)
    fetch_error = pyqtSignal(str)
    status_message = pyqtSignal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._worker: PlaylistFetchWorker | None = None

    def load_file(self, path: str) -> None:
        channels = parse_m3u_file(path)
        self.status_message.emit(t("app.status.channels_loaded", count=len(channels)))
        self.channels_loaded.emit(channels)

    def load_url(self, url: str) -> None:
        self.status_message.emit(t("app.status.fetching"))
        self._worker = PlaylistFetchWorker(url)
        self._worker.fetched.connect(self._on_fetched)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_fetched(self, channels: list[Channel]) -> None:
        self.status_message.emit(t("app.status.channels_loaded", count=len(channels)))
        self.channels_loaded.emit(channels)

    def _on_error(self, message: str) -> None:
        self.status_message.emit(t("app.status.error", message=message))
        self.fetch_error.emit(message)

    def load_profile(self, profile: Profile) -> None:
        if profile.playlist_path:
            self.load_file(profile.playlist_path)
        elif profile.playlist_url:
            self.load_url(profile.playlist_url)
