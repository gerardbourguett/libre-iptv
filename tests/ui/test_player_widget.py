from unittest.mock import MagicMock, patch

import pytest

from src.ui.player_widget import PlayerWidget


@pytest.fixture
def mock_vlc():
    """Patch vlc module so tests don't need real VLC playback."""
    with patch("src.ui.player_widget.vlc") as mock:
        instance = MagicMock()
        player = MagicMock()
        mock.Instance.return_value = instance
        instance.media_player_new.return_value = player
        yield mock, player


@pytest.fixture
def widget(qtbot, mock_vlc):
    w = PlayerWidget()
    qtbot.addWidget(w)
    return w


class TestPlayerWidget:
    def test_play_sets_media_and_plays(self, widget, mock_vlc):
        """S1: play(url) calls set_media + play on the VLC MediaPlayer."""
        _, player = mock_vlc
        url = "http://stream.example.com/cnn"
        widget.play(url)
        player.set_media.assert_called_once()
        player.play.assert_called_once()

    def test_stop_calls_vlc_stop(self, widget, mock_vlc):
        """S2: stop() calls stop on the VLC MediaPlayer."""
        _, player = mock_vlc
        widget.stop()
        player.stop.assert_called_once()

    def test_idle_background_is_black(self, qtbot, mock_vlc):
        """S3: idle player widget has black background."""
        w = PlayerWidget()
        qtbot.addWidget(w)
        style = w.styleSheet()
        assert "background-color: black" in style

    def test_vlc_released_on_close(self, qtbot, mock_vlc):
        """S4: VLC MediaPlayer.release() called when widget is destroyed."""
        _, player = mock_vlc
        w = PlayerWidget()
        qtbot.addWidget(w)
        w.close()
        player.release.assert_called_once()


class TestPlayerWidgetVolume:
    def test_set_volume_calls_vlc_audio_set_volume(self, widget, mock_vlc):
        _, player = mock_vlc
        widget.set_volume(75)
        player.audio_set_volume.assert_called_once_with(75)

    def test_get_volume_returns_vlc_value(self, widget, mock_vlc):
        _, player = mock_vlc
        player.audio_get_volume.return_value = 60
        assert widget.get_volume() == 60

    def test_get_volume_returns_100_when_vlc_returns_minus1(self, widget, mock_vlc):
        _, player = mock_vlc
        player.audio_get_volume.return_value = -1
        assert widget.get_volume() == 100

    def test_toggle_mute_calls_vlc_audio_toggle_mute(self, widget, mock_vlc):
        _, player = mock_vlc
        player.audio_get_mute.return_value = False
        widget.toggle_mute()
        player.audio_toggle_mute.assert_called_once()

    def test_toggle_mute_returns_new_mute_state(self, widget, mock_vlc):
        _, player = mock_vlc
        player.audio_get_mute.return_value = False
        result = widget.toggle_mute()
        assert isinstance(result, bool)
