import vlc
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QCloseEvent, QShowEvent  # noqa: F401
from PyQt6.QtWidgets import QFrame, QWidget


class PlayerWidget(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background-color: black;")
        self._vlc_instance = vlc.Instance()
        self._media_player = self._vlc_instance.media_player_new()
        self._hwnd_bound = False

    def showEvent(self, event: QShowEvent | None) -> None:
        super().showEvent(event)
        if not self._hwnd_bound:
            QTimer.singleShot(0, self._bind_vlc)

    def _bind_vlc(self) -> None:
        self._media_player.set_hwnd(int(self.winId()))
        self._hwnd_bound = True

    def play(self, url: str) -> None:
        media = self._vlc_instance.media_new(url)
        self._media_player.set_media(media)
        self._media_player.play()

    def stop(self) -> None:
        self._media_player.stop()

    def set_volume(self, volume: int) -> None:
        self._media_player.audio_set_volume(volume)

    def get_volume(self) -> int:
        vol = self._media_player.audio_get_volume()
        return 100 if vol == -1 else vol

    def toggle_mute(self) -> bool:
        self._media_player.audio_toggle_mute()
        result = self._media_player.audio_get_mute()
        return bool(result)

    def closeEvent(self, event: QCloseEvent | None) -> None:
        self._media_player.release()
        super().closeEvent(event)
