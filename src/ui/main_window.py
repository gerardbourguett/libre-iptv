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
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from src.models.channel import Channel
from src.parser.m3u import parse_m3u_file, parse_m3u_url
from src.ui.app_settings import AppSettings
from src.ui.channel_list import ChannelListPanel
from src.ui.control_bar import ControlBarWidget
from src.ui.grid_player_widget import GridPlayerWidget

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
        self._grid = GridPlayerWidget()
        self._control_bar = ControlBarWidget()
        self._fetch_worker: PlaylistFetchWorker | None = None

        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_layout.addWidget(self._grid, stretch=1)
        right_layout.addWidget(self._control_bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._channel_list_panel)
        splitter.addWidget(right_container)
        splitter.setSizes([_DEFAULT_LEFT_WIDTH, 620])
        splitter.setHandleWidth(2)
        splitter.setStyleSheet("QSplitter::handle { background: #3a3a3a; }")
        self._splitter = splitter

        # Wire control bar to always route through the active player
        self._control_bar.volume_changed.connect(
            lambda v: self._grid.active_player().set_volume(v)
        )
        self._control_bar.stop_requested.connect(self._grid.stop_active)
        self._control_bar.mute_toggled.connect(
            lambda _: self._grid.active_player().toggle_mute()
        )

        self.setCentralWidget(splitter)

        status_bar = QStatusBar()
        status_bar.setStyleSheet(
            "QStatusBar { background: #1a1a1a; color: #888888; "
            "border-top: 1px solid #3a3a3a; }"
        )
        self.setStatusBar(status_bar)
        status_bar.showMessage("No playlist loaded")

        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)
        self._build_menus(menu_bar)
        self._build_layout_toolbar()

        self._channel_list.channel_selected.connect(self._on_channel_selected)

        self._settings = AppSettings()
        self._restore_settings()

    def _build_layout_toolbar(self) -> None:
        toolbar = QToolBar("Layout")
        toolbar.setMovable(False)
        toolbar.setObjectName("layout_toolbar")

        btn_single = QToolButton()
        btn_single.setText("⬜ 1")
        btn_single.setToolTip("Single view")
        btn_single.clicked.connect(lambda: self._grid.set_mode(1))

        btn_dual = QToolButton()
        btn_dual.setText("⬛ 2")
        btn_dual.setToolTip("Dual view")
        btn_dual.clicked.connect(lambda: self._grid.set_mode(2))

        btn_quad = QToolButton()
        btn_quad.setText("▦ 4")
        btn_quad.setToolTip("Quad view")
        btn_quad.clicked.connect(lambda: self._grid.set_mode(4))

        toolbar.addWidget(btn_single)
        toolbar.addWidget(btn_dual)
        toolbar.addWidget(btn_quad)
        self.addToolBar(toolbar)

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
        playback_menu.addAction("Stop", self._grid.stop_active)

        view_menu = menu_bar.addMenu("View")
        assert view_menu is not None
        layout_menu = view_menu.addMenu("Layout")
        assert layout_menu is not None
        layout_menu.addAction("Single", lambda: self._grid.set_mode(1))
        layout_menu.addAction("Dual", lambda: self._grid.set_mode(2))
        layout_menu.addAction("Quad", lambda: self._grid.set_mode(4))

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
        self._grid.play_in_active(channel.url)
        status_bar = self.statusBar()
        assert status_bar is not None
        status_bar.showMessage(channel.name)
