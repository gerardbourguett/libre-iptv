from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QPixmap
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest


class TestLogoLoader:
    @pytest.fixture
    def loader(self, qtbot):
        from src.ui.logo_loader import LogoLoader

        ll = LogoLoader()
        return ll

    def test_request_dedup_same_url_twice(self, loader):
        """S1: requesting same URL twice only issues one network call."""
        mock_nam = MagicMock(spec=QNetworkAccessManager)
        mock_reply = MagicMock(spec=QNetworkReply)
        mock_reply.error.return_value = QNetworkReply.NetworkError.NoError
        mock_nam.get.return_value = mock_reply
        loader._nam = mock_nam

        loader.request("http://example.com/logo.png")
        loader.request("http://example.com/logo.png")

        assert mock_nam.get.call_count == 1

    def test_request_cache_hit_emits_logo_loaded(self, qtbot, loader):
        """S2: cache hit emits logo_loaded immediately."""
        url = "http://example.com/logo.png"
        loader._cache.put(url, QPixmap(32, 32))

        with qtbot.waitSignal(loader.logo_loaded, timeout=500) as blocker:
            loader.request(url)

        assert blocker.args[0] == url

    def test_request_cache_miss_starts_network(self, loader):
        """S3: cache miss starts a QNetworkReply."""
        mock_nam = MagicMock(spec=QNetworkAccessManager)
        mock_reply = MagicMock(spec=QNetworkReply)
        mock_reply.error.return_value = QNetworkReply.NetworkError.NoError
        mock_nam.get.return_value = mock_reply
        loader._nam = mock_nam

        url = "http://example.com/logo.png"
        loader.request(url)

        mock_nam.get.assert_called_once()
        args, _ = mock_nam.get.call_args
        assert isinstance(args[0], QNetworkRequest)
        assert args[0].url().toString() == url

    def test_timeout_marks_failed(self, qtbot, loader):
        """S4: reply that times out marks URL as failed."""
        from src.ui.logo_loader import LogoLoader

        url = "http://example.com/logo.png"
        mock_nam = MagicMock(spec=QNetworkAccessManager)
        mock_reply = MagicMock(spec=QNetworkReply)
        mock_reply.error.return_value = QNetworkReply.NetworkError.NoError
        mock_nam.get.return_value = mock_reply
        loader._nam = mock_nam

        loader.request(url)

        # Simulate timeout by firing the timer
        with qtbot.waitSignal(loader.logo_loaded, timeout=7000) as blocker:
            loader._timeout_timers[url].timeout.emit()

        assert blocker.args[0] == url
        assert loader.get_pixmap(url) is LogoLoader._FAILED

    def test_get_pixmap_returns_none_while_in_flight(self, loader):
        """S5: get_pixmap returns None while request is in-flight."""
        mock_nam = MagicMock(spec=QNetworkAccessManager)
        mock_reply = MagicMock(spec=QNetworkReply)
        mock_reply.error.return_value = QNetworkReply.NetworkError.NoError
        mock_nam.get.return_value = mock_reply
        loader._nam = mock_nam

        url = "http://example.com/logo.png"
        loader.request(url)

        assert loader.get_pixmap(url) is None

    def test_get_pixmap_returns_cached_pixmap(self, loader):
        """S6: get_pixmap returns QPixmap when cached."""
        url = "http://example.com/logo.png"
        pixmap = QPixmap(32, 32)
        loader._cache.put(url, pixmap)
        assert loader.get_pixmap(url) is pixmap

    def test_finished_with_error_marks_failed(self, qtbot, loader):
        """S7: network error marks URL as failed."""
        from src.ui.logo_loader import LogoLoader

        mock_nam = MagicMock(spec=QNetworkAccessManager)
        mock_reply = MagicMock(spec=QNetworkReply)
        mock_reply.error.return_value = QNetworkReply.NetworkError.HostNotFoundError
        mock_nam.get.return_value = mock_reply
        loader._nam = mock_nam

        url = "http://example.com/logo.png"
        loader.request(url)

        with qtbot.waitSignal(loader.logo_loaded, timeout=1000) as blocker:
            # Simulate finished with error
            reply = mock_nam.get.return_value
            loader._on_reply_finished(reply, url)

        assert blocker.args[0] == url
        assert loader.get_pixmap(url) is LogoLoader._FAILED


class TestLogoLoaderDiskPersistence:
    @pytest.fixture
    def disk_loader(self, qtbot, tmp_path):
        from src.ui.logo_loader import LogoLoader
        return LogoLoader(cache_dir=tmp_path)

    def test_download_saves_to_disk(self, qtbot, disk_loader, tmp_path):
        """Logo downloaded from network is saved to disk cache."""
        from src.ui.logo_loader import LogoLoader
        from PyQt6.QtCore import QBuffer, QIODevice

        url = "http://example.com/logo.png"
        # Generate valid PNG bytes from a real QPixmap
        pixmap = QPixmap(1, 1)
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        pixmap.save(buffer, "PNG")
        png_bytes = bytes(buffer.data())

        mock_nam = MagicMock(spec=QNetworkAccessManager)
        mock_reply = MagicMock(spec=QNetworkReply)
        mock_reply.error.return_value = QNetworkReply.NetworkError.NoError
        mock_reply.readAll.return_value = png_bytes
        mock_nam.get.return_value = mock_reply
        disk_loader._nam = mock_nam

        disk_loader.request(url)
        with qtbot.waitSignal(disk_loader.logo_loaded, timeout=1000):
            disk_loader._on_reply_finished(mock_reply, url)

        # Disk file should exist
        import hashlib
        expected_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
        assert (tmp_path / "logos" / f"{expected_hash}.png").exists()

    def test_second_request_hits_disk_not_network(self, qtbot, disk_loader, tmp_path):
        """Second request for same URL uses disk, skips network."""
        from PyQt6.QtCore import QBuffer, QIODevice

        url = "http://example.com/logo.png"
        # Pre-populate disk cache with valid PNG
        pixmap = QPixmap(1, 1)
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        pixmap.save(buffer, "PNG")
        png_bytes = bytes(buffer.data())

        import hashlib
        expected_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
        logo_dir = tmp_path / "logos"
        logo_dir.mkdir(parents=True, exist_ok=True)
        (logo_dir / f"{expected_hash}.png").write_bytes(png_bytes)

        mock_nam = MagicMock(spec=QNetworkAccessManager)
        disk_loader._nam = mock_nam

        disk_loader.request(url)

        # Should emit immediately without network call
        mock_nam.get.assert_not_called()

    def test_invalidate_removes_from_disk(self, disk_loader, tmp_path):
        """Invalidating a logo removes it from disk cache."""
        url = "http://example.com/logo.png"
        import hashlib
        expected_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
        logo_dir = tmp_path / "logos"
        logo_dir.mkdir(parents=True, exist_ok=True)
        (logo_dir / f"{expected_hash}.png").write_bytes(b"\x89PNG\r\n\x1a\nfakepng")

        disk_loader.invalidate(url)
        assert not (logo_dir / f"{expected_hash}.png").exists()
