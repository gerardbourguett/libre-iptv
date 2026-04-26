from unittest.mock import MagicMock, patch

import pytest

from src.core.vlc_manager import VlcManager
from src.ui.main_window import MainWindow


@pytest.fixture(autouse=True)
def reset_vlc_manager():
    VlcManager._instance = None
    yield


@pytest.fixture
def mock_vlc():
    with patch("src.ui.player_widget.vlc"), patch(
        "src.core.vlc_manager.vlc"
    ) as mock_mgr:
        instance = MagicMock()
        mock_mgr.Instance.return_value = instance
        yield mock_mgr


def test_main_window_close_calls_vlc_manager_release(qtbot, mock_vlc):
    with patch.object(VlcManager, "release") as mock_release:
        window = MainWindow()
        qtbot.addWidget(window)
        window.close()
        mock_release.assert_called_once()
