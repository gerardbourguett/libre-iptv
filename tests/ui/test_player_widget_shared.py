from unittest.mock import MagicMock, patch

from src.ui.player_widget import PlayerWidget


class TestPlayerWidgetSharedInstance:
    def test_injected_instance_not_released_on_close(self, qtbot):
        with patch("src.ui.player_widget.vlc") as mock_vlc:
            shared_instance = MagicMock()
            player = MagicMock()
            shared_instance.media_player_new.return_value = player
            mock_vlc.Instance.return_value = shared_instance

            widget = PlayerWidget(vlc_instance=shared_instance)
            qtbot.addWidget(widget)
            widget.close()
            shared_instance.release.assert_not_called()

    def test_default_instance_released_on_close(self, qtbot):
        with patch("src.ui.player_widget.vlc") as mock_vlc:
            own_instance = MagicMock()
            player = MagicMock()
            own_instance.media_player_new.return_value = player
            mock_vlc.Instance.return_value = own_instance

            widget = PlayerWidget()
            qtbot.addWidget(widget)
            widget.close()
            own_instance.release.assert_called_once()
