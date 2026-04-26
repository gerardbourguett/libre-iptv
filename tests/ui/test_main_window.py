from unittest.mock import MagicMock, patch

import pytest

from src.i18n import init_translator, t
from src.models.channel import Channel
from src.ui.main_window import MainWindow


@pytest.fixture(autouse=True)
def reset_vlc_manager():
    from src.core.vlc_manager import VlcManager

    VlcManager._instance = None
    yield


@pytest.fixture(autouse=True)
def translator(qapp):
    init_translator(locales_dir=None)


@pytest.fixture
def mock_vlc():
    with patch("src.ui.player_widget.vlc") as mock, patch(
        "src.core.vlc_manager.vlc"
    ) as mock_mgr:
        instance = MagicMock()
        player = MagicMock()
        mock.Instance.return_value = instance
        mock_mgr.Instance.return_value = instance
        instance.media_player_new.return_value = player
        yield mock, player


@pytest.fixture
def window(qtbot, mock_vlc):
    w = MainWindow()
    qtbot.addWidget(w)
    return w


class TestMainWindowLayout:
    def test_window_title_is_iptv_player(self, window):
        """S1: window title is 'IPTV Player'."""
        assert window.windowTitle() == t("app.title")

    def test_status_bar_default_message(self, window):
        """S4: default status bar message is 'No playlist loaded'."""
        assert window.statusBar().currentMessage() == t("app.status.no_playlist")


class TestMenuBar:
    def _find_menu(self, window, title: str):
        for action in window.menuBar().actions():
            if action.text() == title:
                return action.menu()
        return None

    def _find_action(self, menu, title: str):
        for action in menu.actions():
            if action.text() == title:
                return action
        return None

    def test_file_menu_exists(self, window):
        """S2: File menu present in menu bar."""
        menu = self._find_menu(window, t("menu.file"))
        assert menu is not None

    def test_file_menu_has_open_playlist(self, window):
        """S2: File menu contains 'Open Playlist'."""
        menu = self._find_menu(window, t("menu.file"))
        action = self._find_action(menu, t("menu.open_playlist"))
        assert action is not None

    def test_file_menu_has_quit(self, window):
        """S2: File menu contains 'Quit'."""
        menu = self._find_menu(window, t("menu.file"))
        action = self._find_action(menu, t("menu.quit"))
        assert action is not None

    def test_playback_menu_has_stop(self, window):
        """S3: Playback menu contains 'Stop'."""
        menu = self._find_menu(window, t("menu.playback"))
        assert menu is not None
        action = self._find_action(menu, t("menu.stop"))
        assert action is not None


class TestSignalWiring:
    def test_channel_selection_updates_status_bar(self, window, qtbot, mock_vlc):
        """S5: selecting a channel updates the status bar with channel name."""
        ch = Channel(url="http://cnn.com", name="CNN International", group="News")
        window._channel_list.channel_selected.emit(ch)
        assert window.statusBar().currentMessage() == "CNN International"


class TestOpenUrl:
    def test_open_url_action_exists_in_file_menu(self, window):
        menu_bar = window.menuBar()
        file_menu = None
        for action in menu_bar.actions():
            if action.text() == t("menu.file"):
                file_menu = action.menu()
                break
        assert file_menu is not None
        action_texts = [a.text() for a in file_menu.actions()]
        assert t("menu.open_url") in action_texts

    def test_open_url_empty_input_does_nothing(self, window, monkeypatch):
        monkeypatch.setattr(
            "src.ui.main_window.QInputDialog.getText",
            lambda *a, **kw: ("", False)
        )
        # Should not raise
        window._open_url()
        status = window.statusBar()
        assert status is not None
        # Status unchanged from initial
        assert status.currentMessage() == t("app.status.no_playlist")

    def test_on_fetch_complete_loads_channels_and_updates_status(self, window):
        from src.models.channel import Channel
        channels = [Channel(url="http://a.com", name="Ch1", group="")]
        window._on_fetch_complete(channels)
        assert window._channel_list.count() > 0
        status = window.statusBar()
        assert status is not None
        assert status.currentMessage() == t("app.status.channels_loaded", count=1)

    def test_on_fetch_error_shows_error_in_status(self, window):
        window._on_fetch_error("Connection refused")
        status = window.statusBar()
        assert status is not None
        assert "Connection refused" in status.currentMessage()

    def test_open_url_shows_fetching_status(self, window, monkeypatch):
        """Status bar shows 'Fetching...' while download is in progress."""
        from unittest.mock import patch

        monkeypatch.setattr(
            "src.ui.main_window.QInputDialog.getText",
            lambda *a, **kw: ("http://example.com/playlist.m3u", True),
        )
        # Patch PlaylistFetchWorker.start in the service so it never actually runs
        with patch("src.services.playlist_service.PlaylistFetchWorker.start"):
            window._open_url()

        status = window.statusBar()
        assert status is not None
        assert status.currentMessage() == t("app.status.fetching")


class TestSettingsIntegration:
    def test_close_event_saves_geometry(self, window, monkeypatch):
        mock_settings = MagicMock()
        window._settings = mock_settings
        from PyQt6.QtGui import QCloseEvent
        event = QCloseEvent()
        window.closeEvent(event)
        mock_settings.save_geometry.assert_called_once()

    def test_close_event_saves_splitter(self, window, monkeypatch):
        mock_settings = MagicMock()
        window._settings = mock_settings
        from PyQt6.QtGui import QCloseEvent
        event = QCloseEvent()
        window.closeEvent(event)
        mock_settings.save_splitter.assert_called_once()

    def test_init_restores_splitter_if_available(self, mock_vlc, qtbot, monkeypatch):
        """If saved splitter sizes exist, they are restored on init."""
        from unittest.mock import MagicMock
        mock_settings = MagicMock()
        mock_settings.load_geometry.return_value = None
        mock_settings.load_splitter.return_value = [200, 500]
        mock_settings.load_last_playlist.return_value = None

        with patch("src.ui.main_window.AppSettings", return_value=mock_settings):
            from src.ui.main_window import MainWindow
            w = MainWindow()
            qtbot.addWidget(w)

        # splitter sizes should reflect the restored values
        mock_settings.load_splitter.assert_called_once()

    def test_open_playlist_saves_last_path(self, window, monkeypatch):
        """After successfully loading a file, the path is saved to settings."""
        from src.models.channel import Channel
        monkeypatch.setattr(
            "src.ui.main_window.QFileDialog.getOpenFileName",
            lambda *a, **kw: ("/home/user/playlist.m3u", ""),
        )
        monkeypatch.setattr(
            "src.services.playlist_service.parse_m3u_file",
            lambda path: [Channel(url="http://a.com", name="Ch1", group="")],
        )
        mock_settings = MagicMock()
        window._settings = mock_settings

        window._open_playlist()

        mock_settings.save_last_playlist.assert_called_once_with("/home/user/playlist.m3u")


class TestVolumeSync:
    def test_active_cell_change_syncs_volume_slider(self, window, mock_vlc):
        """Switching active cell updates the volume slider to that cell's volume."""
        _, player = mock_vlc
        player.audio_get_volume.return_value = 60
        window._grid.set_mode(4)
        window._grid._on_cell_clicked(1)
        assert window._control_bar.volume_slider.value() == 60


class TestLayoutSwitcher:
    def test_window_has_grid_attribute(self, window):
        """MainWindow exposes _grid (GridPlayerWidget)."""
        from src.ui.grid_player_widget import GridPlayerWidget
        assert hasattr(window, "_grid")
        assert isinstance(window._grid, GridPlayerWidget)

    def test_layout_toolbar_has_three_buttons(self, window):
        """Layout toolbar has Single, Dual, and Quad buttons."""
        from PyQt6.QtWidgets import QToolButton
        buttons = window.findChildren(QToolButton)
        labels = [b.text() for b in buttons]
        assert any("1" in t or "Single" in t or "⬜" in t for t in labels)
        assert any("2" in t or "Dual" in t or "⬛" in t for t in labels)
        assert any("4" in t or "Quad" in t or "▦" in t for t in labels)

    def test_view_menu_exists(self, window):
        """A View menu is present in the menu bar."""
        menu_bar = window.menuBar()
        texts = [a.text() for a in menu_bar.actions()]
        assert t("menu.view") in texts


class TestMainWindowMenu:
    def test_help_menu_exists(self, window):
        menu_bar = window.menuBar()
        texts = [a.text() for a in menu_bar.actions()]
        assert t("menu.help") in texts

    def test_acerca_de_action_exists(self, window):
        menu_bar = window.menuBar()
        help_menu = None
        for action in menu_bar.actions():
            if action.text() == t("menu.help"):
                help_menu = action.menu()
                break
        assert help_menu is not None
        action_texts = [a.text() for a in help_menu.actions()]
        assert t("menu.about") in action_texts

    def test_acerca_de_action_opens_about_dialog(self, window):
        from unittest.mock import MagicMock, patch

        mock_dialog_cls = MagicMock()
        with patch("src.ui.about_dialog.AboutDialog", mock_dialog_cls):
            menu_bar = window.menuBar()
            help_menu = None
            for action in menu_bar.actions():
                if action.text() == t("menu.help"):
                    help_menu = action.menu()
                    break
            assert help_menu is not None

            acerca_action = None
            for action in help_menu.actions():
                if action.text() == t("menu.about"):
                    acerca_action = action
                    break
            assert acerca_action is not None

            acerca_action.trigger()

        mock_dialog_cls.assert_called_once_with(parent=window)
        mock_dialog_cls.return_value.exec.assert_called_once()


class TestDarkTheme:
    def test_configure_app_sets_fusion_style(self, qtbot):
        """configure_app applies Fusion style to the QApplication."""
        from PyQt6.QtWidgets import QApplication

        from main import configure_app

        configure_app(QApplication.instance())
        assert QApplication.style().objectName() == "fusion"

    def test_status_bar_has_stylesheet(self, window):
        """Status bar has a custom stylesheet applied."""
        status_bar = window.statusBar()
        assert status_bar is not None
        assert len(status_bar.styleSheet()) > 0


class TestOpenPlaylist:
    def test_open_playlist_dialog_uses_correct_filter(self, window, monkeypatch):
        """Dialog is opened with the M3U file filter."""
        mock_dialog = MagicMock(return_value=("", ""))
        monkeypatch.setattr(
            "src.ui.main_window.QFileDialog.getOpenFileName", mock_dialog
        )

        window._open_playlist()

        assert t("dialog.playlist_filter") in str(mock_dialog.call_args)

    def test_open_playlist_loads_channels_and_updates_status(
        self, window, monkeypatch
    ):
        """Valid file path: channels are loaded and status bar updated."""
        monkeypatch.setattr(
            "src.ui.main_window.QFileDialog.getOpenFileName",
            MagicMock(return_value=("/path/test.m3u", "")),
        )
        monkeypatch.setattr(
            "src.services.playlist_service.parse_m3u_file",
            MagicMock(
                return_value=[Channel(url="http://a.com", name="TestCh", group="")]
            ),
        )

        window._open_playlist()

        assert window._channel_list.count() > 0
        assert window.statusBar().currentMessage() == t(
            "app.status.channels_loaded", count=1
        )

    def test_open_playlist_cancel_does_not_change_state(self, window, monkeypatch):
        """Cancelling the dialog leaves channel list and status bar unchanged."""
        monkeypatch.setattr(
            "src.ui.main_window.QFileDialog.getOpenFileName",
            MagicMock(return_value=("", "")),
        )
        load_channels_mock = MagicMock()
        monkeypatch.setattr(window._channel_list, "load_channels", load_channels_mock)

        window._open_playlist()

        assert load_channels_mock.call_count == 0
        assert window.statusBar().currentMessage() == t("app.status.no_playlist")
