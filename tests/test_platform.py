from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.platform import (
    APP_NAME,
    bind_vlc,
    check_vlc,
    get_config_dir,
    migrate_from_legacy,
)


class TestGetConfigDir:
    @pytest.mark.parametrize(
        ("platform", "mock_path"),
        [
            ("win32", r"C:\Users\Mock\AppData\Roaming\iptv-player"),
            ("darwin", "/Users/mock/Library/Application Support/iptv-player"),
            ("linux", "/home/mock/.config/iptv-player"),
        ],
    )
    def test_returns_correct_path_per_os(self, platform, mock_path, monkeypatch):
        monkeypatch.setattr(sys, "platform", platform)
        with patch(
            "src.platform.user_config_dir", return_value=mock_path
        ) as mock_dir:
            with patch.object(Path, "mkdir"):
                result = get_config_dir()
                mock_dir.assert_called_once_with(APP_NAME)
                assert result == Path(mock_path)

    def test_creates_directory_if_missing(self, monkeypatch, tmp_path: Path):
        monkeypatch.setattr(sys, "platform", "linux")
        target = tmp_path / "new_config" / "iptv-player"
        with patch("src.platform.user_config_dir", return_value=str(target)):
            result = get_config_dir()
            assert result.exists()
            assert result.is_dir()


class TestBindVlc:
    @pytest.mark.parametrize(
        ("platform", "expected_method"),
        [
            ("win32", "set_hwnd"),
            ("darwin", "set_nsobject"),
            ("linux", "set_xid"),
        ],
    )
    def test_calls_correct_method_per_platform(
        self, platform, expected_method, monkeypatch
    ):
        monkeypatch.setattr(sys, "platform", platform)
        player = MagicMock()
        bind_vlc(player, 12345)
        getattr(player, expected_method).assert_called_once_with(12345)

    def test_raises_on_unknown_platform(self, monkeypatch):
        monkeypatch.setattr(sys, "platform", "freebsd")
        player = MagicMock()
        with pytest.raises(RuntimeError, match="Unsupported platform"):
            bind_vlc(player, 12345)


class TestCheckVlc:
    @pytest.mark.parametrize(
        ("platform", "expected_cmd"),
        [
            ("win32", "choco install vlc"),
            ("darwin", "brew install --cask vlc"),
            ("linux", "sudo apt install vlc"),
        ],
    )
    def test_raises_import_error_with_platform_instructions(
        self, platform, expected_cmd, monkeypatch
    ):
        monkeypatch.setattr(sys, "platform", platform)
        with patch("src.platform.vlc") as mock_vlc:
            mock_vlc.Instance.side_effect = ImportError("No VLC")
            with pytest.raises(ImportError, match=expected_cmd):
                check_vlc()

    def test_does_not_raise_when_vlc_available(self):
        with patch("src.platform.vlc") as mock_vlc:
            mock_vlc.Instance.return_value = MagicMock()
            check_vlc()


class TestMigrateFromLegacy:
    def test_copies_on_windows_when_legacy_exists_and_new_missing(
        self, monkeypatch, tmp_path: Path
    ):
        monkeypatch.setattr(sys, "platform", "win32")
        home = tmp_path / "home"
        home.mkdir()
        legacy = home / ".config" / APP_NAME / "profiles"
        legacy.mkdir(parents=True)
        (legacy / "index.json").write_text("[]")
        new_dir = tmp_path / "appdata" / APP_NAME / "profiles"

        with patch("src.platform.get_config_dir", return_value=new_dir.parent):
            with patch.object(Path, "home", return_value=home):
                migrate_from_legacy()
                assert (new_dir / "index.json").exists()
                assert (legacy / "index.json").exists()

    def test_skips_when_new_dir_already_exists(self, monkeypatch, tmp_path: Path):
        monkeypatch.setattr(sys, "platform", "win32")
        home = tmp_path / "home"
        home.mkdir()
        legacy = home / ".config" / APP_NAME / "profiles"
        legacy.mkdir(parents=True)
        new_dir = tmp_path / "appdata" / APP_NAME / "profiles"
        new_dir.mkdir(parents=True)

        with patch("src.platform.shutil.copytree") as mock_copy:
            with patch("src.platform.get_config_dir", return_value=new_dir.parent):
                with patch.object(Path, "home", return_value=home):
                    migrate_from_legacy()
                    mock_copy.assert_not_called()

    def test_noop_on_windows_when_legacy_missing(self, monkeypatch, tmp_path: Path):
        monkeypatch.setattr(sys, "platform", "win32")
        home = tmp_path / "home"
        home.mkdir()
        with patch("src.platform.shutil.copytree") as mock_copy:
            with patch("src.platform.get_config_dir") as mock_get_dir:
                with patch.object(Path, "home", return_value=home):
                    migrate_from_legacy()
                    mock_copy.assert_not_called()
                    mock_get_dir.assert_not_called()

    def test_noop_on_non_windows(self, monkeypatch, tmp_path: Path):
        monkeypatch.setattr(sys, "platform", "darwin")
        with patch("src.platform.shutil.copytree") as mock_copy:
            migrate_from_legacy()
            mock_copy.assert_not_called()
