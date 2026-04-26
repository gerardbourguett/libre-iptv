from __future__ import annotations

from unittest.mock import MagicMock, Mock

from src.services.playlist_service import PlaylistService


class TestPlaylistServiceLoadFile:
    def test_load_file_emits_channels_loaded(self, qtbot, monkeypatch):
        """load_file parses file and emits channels_loaded with list[Channel]."""
        from src.models.channel import Channel

        channels = [Channel(url="http://a.com", name="A", group="")]
        monkeypatch.setattr(
            "src.services.playlist_service.parse_m3u_file", lambda path: channels
        )
        service = PlaylistService()
        with qtbot.waitSignal(service.channels_loaded, timeout=1000) as blocker:
            service.load_file("/path/list.m3u")
        assert blocker.args[0] == channels

    def test_load_file_emits_status_message(self, qtbot, monkeypatch):
        """load_file emits a status_message signal."""
        from src.models.channel import Channel

        channels = [Channel(url="http://a.com", name="A", group="")]
        monkeypatch.setattr(
            "src.services.playlist_service.parse_m3u_file", lambda path: channels
        )
        service = PlaylistService()
        with qtbot.waitSignal(service.status_message, timeout=1000) as blocker:
            service.load_file("/path/list.m3u")
        assert isinstance(blocker.args[0], str)


class TestPlaylistServiceLoadUrl:
    def test_load_url_creates_worker_and_emits_channels_loaded(
        self, qtbot, monkeypatch
    ):
        """load_url creates worker and emits channels_loaded on complete."""
        from src.models.channel import Channel

        channels = [Channel(url="http://a.com", name="A", group="")]
        mock_worker_cls = MagicMock()
        instance = MagicMock()
        mock_worker_cls.return_value = instance
        monkeypatch.setattr(
            "src.services.playlist_service.PlaylistFetchWorker", mock_worker_cls
        )

        service = PlaylistService()

        fetched_slot = None

        def capture_fetched_connect(slot):
            nonlocal fetched_slot
            fetched_slot = slot

        instance.fetched.connect = capture_fetched_connect
        instance.error.connect = Mock()

        with qtbot.waitSignal(service.channels_loaded, timeout=1000) as blocker:
            service.load_url("http://example.com/list.m3u")
            assert fetched_slot is not None
            fetched_slot(channels)

        mock_worker_cls.assert_called_once_with("http://example.com/list.m3u")
        instance.start.assert_called_once()
        assert blocker.args[0] == channels

    def test_load_url_emits_fetch_error_on_failure(self, qtbot, monkeypatch):
        """load_url emits fetch_error when worker reports an error."""
        mock_worker_cls = MagicMock()
        instance = MagicMock()
        mock_worker_cls.return_value = instance
        monkeypatch.setattr(
            "src.services.playlist_service.PlaylistFetchWorker", mock_worker_cls
        )

        service = PlaylistService()

        error_slot = None

        def capture_error_connect(slot):
            nonlocal error_slot
            error_slot = slot

        instance.fetched.connect = Mock()
        instance.error.connect = capture_error_connect

        with qtbot.waitSignal(service.fetch_error, timeout=1000) as blocker:
            service.load_url("http://example.com/list.m3u")
            assert error_slot is not None
            error_slot("Connection refused")

        assert blocker.args[0] == "Connection refused"

    def test_load_url_emits_status_message(self, qtbot, monkeypatch):
        """load_url emits a status_message signal indicating fetch started."""
        mock_worker_cls = MagicMock()
        instance = MagicMock()
        mock_worker_cls.return_value = instance
        monkeypatch.setattr(
            "src.services.playlist_service.PlaylistFetchWorker", mock_worker_cls
        )
        instance.fetched.connect = Mock()
        instance.error.connect = Mock()

        service = PlaylistService()
        with qtbot.waitSignal(service.status_message, timeout=1000) as blocker:
            service.load_url("http://example.com/list.m3u")
        assert isinstance(blocker.args[0], str)


class TestPlaylistServiceLoadProfile:
    def test_load_profile_with_path_calls_load_file(self, monkeypatch):
        """load_profile resolves playlist_path and delegates to load_file."""
        from src.models.profile import Profile

        profile = Profile(
            id="1", name="P", color="#000", playlist_path="/local.m3u"
        )
        calls = []
        monkeypatch.setattr(
            PlaylistService,
            "load_file",
            lambda self, path: calls.append(("file", path)),
        )
        monkeypatch.setattr(
            PlaylistService,
            "load_url",
            lambda self, url: calls.append(("url", url)),
        )
        service = PlaylistService()
        service.load_profile(profile)
        assert calls == [("file", "/local.m3u")]

    def test_load_profile_with_url_calls_load_url(self, monkeypatch):
        """load_profile resolves playlist_url and delegates to load_url."""
        from src.models.profile import Profile

        profile = Profile(
            id="1", name="P", color="#000", playlist_url="http://remote.m3u"
        )
        calls = []
        monkeypatch.setattr(
            PlaylistService,
            "load_file",
            lambda self, path: calls.append(("file", path)),
        )
        monkeypatch.setattr(
            PlaylistService,
            "load_url",
            lambda self, url: calls.append(("url", url)),
        )
        service = PlaylistService()
        service.load_profile(profile)
        assert calls == [("url", "http://remote.m3u")]

    def test_load_profile_with_neither_does_nothing(self, monkeypatch):
        """load_profile with no playlist config does nothing."""
        from src.models.profile import Profile

        profile = Profile(id="1", name="P", color="#000")
        calls = []
        monkeypatch.setattr(
            PlaylistService,
            "load_file",
            lambda self, path: calls.append(("file", path)),
        )
        monkeypatch.setattr(
            PlaylistService,
            "load_url",
            lambda self, url: calls.append(("url", url)),
        )
        service = PlaylistService()
        service.load_profile(profile)
        assert calls == []
