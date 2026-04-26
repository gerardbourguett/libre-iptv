from unittest.mock import MagicMock, patch

import pytest

from src.core.vlc_manager import VlcManager


class TestVlcManager:
    @pytest.fixture(autouse=True)
    def reset_manager(self):
        VlcManager._instance = None
        yield

    def test_first_call_creates_instance(self):
        with patch("src.core.vlc_manager.vlc") as mock_vlc:
            mock_instance = MagicMock()
            mock_vlc.Instance.return_value = mock_instance
            result = VlcManager.get_instance()
            mock_vlc.Instance.assert_called_once()
            assert result is mock_instance

    def test_subsequent_calls_return_same_instance(self):
        with patch("src.core.vlc_manager.vlc") as mock_vlc:
            mock_instance = MagicMock()
            mock_vlc.Instance.return_value = mock_instance
            first = VlcManager.get_instance()
            second = VlcManager.get_instance()
            assert first is second
            mock_vlc.Instance.assert_called_once()

    def test_release_resets_singleton(self):
        with patch("src.core.vlc_manager.vlc") as mock_vlc:
            mock_instance = MagicMock()
            mock_vlc.Instance.return_value = mock_instance
            VlcManager.get_instance()
            VlcManager.release()
            mock_instance.release.assert_called_once()
            assert VlcManager._instance is None

    def test_release_idempotent(self):
        with patch("src.core.vlc_manager.vlc") as mock_vlc:
            mock_instance = MagicMock()
            mock_vlc.Instance.return_value = mock_instance
            VlcManager.get_instance()
            VlcManager.release()
            VlcManager.release()
            mock_instance.release.assert_called_once()
            assert VlcManager._instance is None
