import pytest
from PyQt6.QtCore import QByteArray, QSettings

from src.ui.app_settings import AppSettings


@pytest.fixture
def settings(tmp_path, monkeypatch):
    """AppSettings backed by a temp INI file for test isolation."""
    ini_path = tmp_path / "test_settings.ini"
    qs = QSettings(str(ini_path), QSettings.Format.IniFormat)
    return AppSettings(settings=qs)


class TestAppSettingsGeometry:
    def test_save_and_load_geometry(self, settings):
        data = QByteArray(b"\x00\x01\x02\x03")
        settings.save_geometry(data)
        result = settings.load_geometry()
        assert result == data

    def test_load_geometry_returns_none_when_not_set(self, settings):
        assert settings.load_geometry() is None


class TestAppSettingsSplitter:
    def test_save_and_load_splitter(self, settings):
        sizes = [280, 620]
        settings.save_splitter(sizes)
        result = settings.load_splitter()
        assert result == sizes

    def test_load_splitter_returns_none_when_not_set(self, settings):
        assert settings.load_splitter() is None


class TestAppSettingsLastPlaylist:
    def test_save_and_load_last_playlist(self, settings):
        settings.save_last_playlist("/home/user/playlist.m3u")
        assert settings.load_last_playlist() == "/home/user/playlist.m3u"

    def test_load_last_playlist_returns_none_when_not_set(self, settings):
        assert settings.load_last_playlist() is None
