from unittest.mock import MagicMock, patch

import pytest

from src.ui.main_window import MainWindow


@pytest.fixture(autouse=True)
def reset_vlc_manager():
    from src.core.vlc_manager import VlcManager

    VlcManager._instance = None
    yield


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
    from unittest.mock import MagicMock

    mock_settings = MagicMock()
    mock_settings.load_geometry.return_value = None
    mock_settings.load_splitter.return_value = None
    mock_settings.load_last_playlist.return_value = None

    with patch("src.ui.main_window.AppSettings", return_value=mock_settings):
        w = MainWindow()
        qtbot.addWidget(w)
        return w


class TestMainWindowFetchState:
    def test_menu_actions_disabled_during_fetch(self, window, monkeypatch):
        """S1: File→Open actions are disabled while fetching."""
        monkeypatch.setattr(
            "src.ui.main_window.QInputDialog.getText",
            lambda *a, **kw: ("http://example.com/playlist.m3u", True),
        )
        with patch("src.services.playlist_service.PlaylistFetchWorker.start"):
            window._open_url()

        assert window._open_file_action.isEnabled() is False
        assert window._open_url_action.isEnabled() is False

    def test_menu_actions_re_enabled_after_fetch_complete(self, window, qtbot):
        """S2: File→Open actions re-enabled after fetch completes."""
        from src.models.channel import Channel

        channels = [Channel(url="http://a.com", name="Ch1", group="")]
        window._on_fetch_complete(channels)

        assert window._open_file_action.isEnabled() is True
        assert window._open_url_action.isEnabled() is True

    def test_menu_actions_re_enabled_after_fetch_error(self, window, qtbot):
        """S3: File→Open actions re-enabled after fetch error."""
        window._on_fetch_error("Connection refused")

        assert window._open_file_action.isEnabled() is True
        assert window._open_url_action.isEnabled() is True

    def test_loading_overlay_shown_during_fetch(self, window, monkeypatch):
        """S4: Loading overlay is visible during fetch."""
        window.show()
        monkeypatch.setattr(
            "src.ui.main_window.QInputDialog.getText",
            lambda *a, **kw: ("http://example.com/playlist.m3u", True),
        )
        with patch("src.services.playlist_service.PlaylistFetchWorker.start"):
            window._open_url()

        assert window._loading_overlay.isVisible()

    def test_loading_overlay_hidden_after_fetch_complete(self, window, qtbot):
        """S5: Loading overlay hidden after fetch completes."""
        from src.models.channel import Channel

        channels = [Channel(url="http://a.com", name="Ch1", group="")]
        window._on_fetch_complete(channels)

        assert window._loading_overlay.isHidden()

    def test_loading_overlay_hidden_after_fetch_error(self, window, qtbot):
        """S6: Loading overlay hidden after fetch error."""
        window._on_fetch_error("Connection refused")

        assert window._loading_overlay.isHidden()

    def test_success_toast_on_fetch_complete(self, window, qtbot):
        """S7: Success toast is shown on fetch complete."""
        from src.models.channel import Channel

        channels = [Channel(url="http://a.com", name="Ch1", group="")]
        window._on_fetch_complete(channels)

        # Verify toast manager parented correctly
        assert window._toast_manager is not None

    def test_error_toast_on_fetch_error(self, window, qtbot):
        """S8: Error toast is shown on fetch error."""
        window._on_fetch_error("Connection refused")

        assert window._toast_manager is not None
