from unittest.mock import MagicMock, patch

import pytest

from src.ui.player_widget import PlayerWidget


@pytest.fixture
def mock_vlc():
    with patch("src.ui.player_widget.vlc") as mock:
        instance = MagicMock()
        player = MagicMock()
        mock.Instance.return_value = instance
        instance.media_player_new.return_value = player
        yield mock, player


class TestPlayerWidgetPlaceholder:
    def test_placeholder_visible_on_init(self, qtbot, mock_vlc):
        """S1: Placeholder QLabel is visible when PlayerWidget is created."""
        widget = PlayerWidget()
        qtbot.addWidget(widget)
        widget.show()
        assert widget._placeholder.isVisible()

    def test_placeholder_hidden_after_play(self, qtbot, mock_vlc):
        """S2: Placeholder is hidden after play() is called."""
        widget = PlayerWidget()
        qtbot.addWidget(widget)
        widget.play("http://stream.example.com/test")
        assert widget._placeholder.isHidden()

    def test_placeholder_text_is_spanish(self, qtbot, mock_vlc):
        """S3: Placeholder text uses neutral Spanish."""
        widget = PlayerWidget()
        qtbot.addWidget(widget)
        assert "Selecciona" in widget._placeholder.text() or "Reproduce" in widget._placeholder.text()
