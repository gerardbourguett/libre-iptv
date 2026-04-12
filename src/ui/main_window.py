from pathlib import Path

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QKeyEvent
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
from src.models.profile import Profile
from src.parser.m3u import fetch_best_playlist, parse_m3u_file
from src.profiles.manager import ProfileManager
from src.ui.app_settings import AppSettings
from src.ui.channel_list import ChannelListPanel
from src.ui.control_bar import ControlBarWidget
from src.ui.grid_player_widget import GridPlayerWidget
from src.ui.profile_bar import ProfileSelectorBar

_DEFAULT_LEFT_WIDTH = 280


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


class MainWindow(QMainWindow):
    def __init__(
        self,
        manager: ProfileManager | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._manager = manager
        self.setWindowTitle("IPTV Player")
        self.setMinimumSize(900, 600)

        self._channel_list_panel = ChannelListPanel(manager=manager)
        self._channel_list = self._channel_list_panel.channel_list
        self._grid = GridPlayerWidget()
        self._control_bar = ControlBarWidget()
        self._fetch_worker: PlaylistFetchWorker | None = None

        # Left panel: profile bar (if manager) + channel list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        if manager is not None:
            self._profile_bar = ProfileSelectorBar(manager)
            self._profile_bar.profile_switched.connect(self._on_profile_switched)
            left_layout.addWidget(self._profile_bar)
        left_layout.addWidget(self._channel_list_panel)

        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_layout.addWidget(self._grid, stretch=1)
        right_layout.addWidget(self._control_bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
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
        self._channel_list.favorite_toggled.connect(self._on_favorite_toggled)
        self._grid.active_cell_changed.connect(self._on_active_cell_changed)

        self._channels: list[Channel] = []
        self._fullscreen: bool = False
        self._settings = AppSettings()
        self._restore_settings()

        if manager is not None:
            self._auto_load_profile(manager.active_profile())

    def _build_layout_toolbar(self) -> None:
        toolbar = QToolBar("Layout")
        toolbar.setMovable(False)
        toolbar.setObjectName("layout_toolbar")
        toolbar.setStyleSheet(
            "QToolBar { background: #0d0d0d;"
            " border-bottom: 1px solid #1e1e1e;"
            " spacing: 4px; padding: 4px 8px; }"
            "QToolButton { background: #1e1e1e; color: #9e9e9e;"
            " border: 1px solid #2a2a2a; border-radius: 6px;"
            " padding: 4px 14px; font-size: 13px; }"
            "QToolButton:hover { background: #262626; color: #e0e0e0; }"
            "QToolButton:checked { background: #00bcd4;"
            " color: #000000; border-color: #00bcd4; }"
        )

        self._layout_buttons: dict[int, QToolButton] = {}
        _modes = [(1, "⬜  1", "Single"), (2, "⬛  2", "Dual"), (4, "▦  4", "Quad")]
        for mode, label, tip in _modes:
            btn = QToolButton()
            btn.setText(label)
            btn.setToolTip(f"{tip} view")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, m=mode: self._set_layout_mode(m))
            toolbar.addWidget(btn)
            self._layout_buttons[mode] = btn

        self._layout_buttons[1].setChecked(True)
        self.addToolBar(toolbar)

    def _set_layout_mode(self, mode: int) -> None:
        self._grid.set_mode(mode)
        for m, btn in self._layout_buttons.items():
            btn.setChecked(m == mode)

    def _auto_load_profile(self, profile: Profile) -> None:
        """Load playlist for the given profile if one is configured."""
        if profile.playlist_path:
            channels = parse_m3u_file(Path(profile.playlist_path))
            self._channels = channels
            self._reload_channel_list()
            sb = self.statusBar()
            if sb:
                sb.showMessage(f"{len(channels)} channels loaded")
        elif profile.playlist_url:
            sb = self.statusBar()
            if sb:
                sb.showMessage("Fetching playlist...")
            self._fetch_worker = PlaylistFetchWorker(profile.playlist_url)
            self._fetch_worker.fetched.connect(self._on_fetch_complete)
            self._fetch_worker.error.connect(self._on_fetch_error)
            self._fetch_worker.start()

    def _reload_channel_list(self) -> None:
        """Reload the channel list with current profile's favorites and recent."""
        favorites: list[str] = []
        recent: list[str] = []
        if self._manager is not None:
            profile = self._manager.active_profile()
            favorites = profile.favorites
            recent = profile.recent
        self._channel_list.load_channels(
            self._channels, favorites=favorites, recent=recent
        )

    def _on_profile_switched(self, profile: Profile) -> None:
        """Handle profile switch: stop playback, clear list, auto-load new playlist."""
        self._grid.stop_active()
        self._channels = []
        self._channel_list.load_channels([])
        self._auto_load_profile(profile)
        if hasattr(self, "_profile_bar"):
            self._profile_bar.refresh()

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
        if self._manager is not None:
            self._manager.save_active()
        super().closeEvent(event)

    def keyPressEvent(self, event: QKeyEvent | None) -> None:
        if event is None:
            return
        key = event.key()
        text = event.text()

        if key == Qt.Key.Key_F11 or (key == Qt.Key.Key_F and not text):
            self._toggle_fullscreen()
        elif key == Qt.Key.Key_Escape and self._fullscreen:
            self._fullscreen = False
            self.showNormal()
        elif text == "1":
            self._set_layout_mode(1)
        elif text == "2":
            self._set_layout_mode(2)
        elif text == "4":
            self._set_layout_mode(4)
        elif key == Qt.Key.Key_M:
            self._grid.active_player().toggle_mute()
        elif key == Qt.Key.Key_Space:
            self._grid.stop_active()
        else:
            super().keyPressEvent(event)

    def _toggle_fullscreen(self) -> None:
        if self._fullscreen:
            self._fullscreen = False
            self.showNormal()
        else:
            self._fullscreen = True
            self.showFullScreen()

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
        self._channels = channels
        self._reload_channel_list()
        status_bar = self.statusBar()
        assert status_bar is not None
        status_bar.showMessage(f"{len(channels)} channels loaded")

    def _on_favorite_toggled(self, channel_url: str) -> None:
        if self._manager is None:
            return
        self._manager.toggle_favorite(channel_url)
        self._manager.save_active()
        self._channel_list.reload_with_profile(self._manager.active_profile())

    def _on_fetch_error(self, message: str) -> None:
        status_bar = self.statusBar()
        assert status_bar is not None
        status_bar.showMessage(f"Error: {message}")

    def _on_active_cell_changed(self, index: int) -> None:  # noqa: ARG002
        volume = self._grid.active_player().get_volume()
        self._control_bar.volume_slider.blockSignals(True)
        self._control_bar.volume_slider.setValue(volume)
        self._control_bar.volume_slider.blockSignals(False)

    def _on_channel_selected(self, channel: Channel) -> None:
        self._grid.play_in_active(channel.url)
        if self._manager is not None:
            self._manager.add_to_recent(channel.url)
            self._manager.save_active()
        status_bar = self.statusBar()
        assert status_bar is not None
        status_bar.showMessage(channel.name)
