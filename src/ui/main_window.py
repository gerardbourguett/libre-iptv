from pathlib import Path

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QInputDialog,
    QMainWindow,
    QMenuBar,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from src.models.channel import Channel
from src.parser.m3u import parse_m3u_file, parse_m3u_url
from src.ui.app_settings import AppSettings
from src.ui.channel_list import ChannelListPanel
from src.ui.control_bar import ControlBarWidget
from src.ui.player_widget import PlayerWidget

_DEFAULT_LEFT_WIDTH = 280


class PlaylistFetchWorker(QThread):
    fetched: pyqtSignal = pyqtSignal(list)
    error: pyqtSignal = pyqtSignal(str)

    def __init__(self, url: str) -> None:
        super().__init__()
        self._url = url

    def run(self) -> None:
        try:
            channels = parse_m3u_url(self._url)
            self.fetched.emit(channels)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("IPTV Player")
        self.setMinimumSize(900, 600)

        self._channel_list_panel = ChannelListPanel()
        self._channel_list = self._channel_list_panel.channel_list
        self._player = PlayerWidget()
        self._control_bar = ControlBarWidget()
        self._fetch_worker: PlaylistFetchWorker | None = None

        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_layout.addWidget(self._player, stretch=1)
        right_layout.addWidget(self._control_bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._channel_list_panel)
        splitter.addWidget(right_container)
        splitter.setSizes([_DEFAULT_LEFT_WIDTH, 620])
        self._splitter = splitter

        self._control_bar.volume_changed.connect(self._player.set_volume)
        self._control_bar.stop_requested.connect(self._player.stop)
        self._control_bar.mute_toggled.connect(lambda _: self._player.toggle_mute())

        self.setCentralWidget(splitter)

        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage("No playlist loaded")

        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)
        self._build_menus(menu_bar)

        self._channel_list.channel_selected.connect(self._on_channel_selected)

        self._settings = AppSettings()
        self._restore_settings()

    def _restore_settings(self) -> None:
        geometry = self._settings.load_geometry()
        if geometry is not None:
            self.restoreGeometry(geometry)
        sizes = self._settings.load_splitter()
        if sizes is not None:
            self._splitter.setSizes(sizes)

    def closeEvent(self, event: QCloseEvent | None) -> None:
        self._settings.save_geometry(self.saveGeometry())
        self._settings.save_splitter(self._splitter.sizes())
        super().closeEvent(event)

    def _build_menus(self, menu_bar: QMenuBar) -> None:
        file_menu = menu_bar.addMenu("File")
        assert file_menu is not None
        file_menu.addAction("Open Playlist", self._open_playlist)
        file_menu.addAction("Open URL...", self._open_url)
        file_menu.addSeparator()
        file_menu.addAction("Quit", QApplication.quit)

        playback_menu = menu_bar.addMenu("Playback")
        assert playback_menu is not None
        playback_menu.addAction("Stop", self._player.stop)

    def _open_playlist(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Playlist",
            "",
            "M3U Playlists (*.m3u *.m3u8)",
        )
        if not path:
            return
        channels = parse_m3u_file(Path(path))
        self._channel_list.load_channels(channels)
        status_bar = self.statusBar()
        assert status_bar is not None
        status_bar.showMessage(f"{len(channels)} channels loaded")
        self._settings.save_last_playlist(path)

    def _open_url(self) -> None:
        url, ok = QInputDialog.getText(self, "Open URL", "Enter M3U URL:")
        if not ok or not url.strip():
            return
        status_bar = self.statusBar()
        assert status_bar is not None
        status_bar.showMessage("Fetching...")
        self._fetch_worker = PlaylistFetchWorker(url.strip())
        self._fetch_worker.fetched.connect(self._on_fetch_complete)
        self._fetch_worker.error.connect(self._on_fetch_error)
        self._fetch_worker.start()

    def _on_fetch_complete(self, channels: list[Channel]) -> None:
        self._channel_list.load_channels(channels)
        status_bar = self.statusBar()
        assert status_bar is not None
        status_bar.showMessage(f"{len(channels)} channels loaded")

    def _on_fetch_error(self, message: str) -> None:
        status_bar = self.statusBar()
        assert status_bar is not None
        status_bar.showMessage(f"Error: {message}")

    def _on_channel_selected(self, channel: Channel) -> None:
        self._player.play(channel.url)
        status_bar = self.statusBar()
        assert status_bar is not None
        status_bar.showMessage(channel.name)
