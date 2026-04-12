import vlc
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QMouseEvent, QShowEvent  # noqa: F401
from PyQt6.QtWidgets import QFrame, QWidget


class PlayerWidget(QFrame):
    clicked = pyqtSignal()

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

    def mousePressEvent(self, event: QMouseEvent | None) -> None:
        self.clicked.emit()
        super().mousePressEvent(event)

    def set_active(self, active: bool) -> None:
        if active:
            self.setStyleSheet(
                "background-color: black; border: 2px solid #0d6efd;"
            )
        else:
            self.setStyleSheet("background-color: black;")

    def play(self, url: str) -> None:
        if not self._hwnd_bound:
            self._bind_vlc()
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
