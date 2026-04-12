import pytest

from src.models.channel import Channel


class TestChannelCreation:
    def test_all_fields(self) -> None:
        """S1: Channel with all fields."""
        ch = Channel(
            url="rtsp://stream.example.com/cnn",
            name="CNN",
            tvg_id="cnn",
            tvg_name="CNN International",
            tvg_logo="http://logo.com/cnn.png",
            group="News",
        )
        assert ch.url == "rtsp://stream.example.com/cnn"
        assert ch.name == "CNN"
        assert ch.tvg_id == "cnn"
        assert ch.tvg_name == "CNN International"
        assert ch.tvg_logo == "http://logo.com/cnn.png"
        assert ch.group == "News"

    def test_only_required_fields(self) -> None:
        """S2: Channel with only required fields defaults the rest."""
        ch = Channel(url="http://stream.example.com/live", name="My Channel")
        assert ch.url == "http://stream.example.com/live"
        assert ch.name == "My Channel"
        assert ch.tvg_id == ""
        assert ch.tvg_name == ""
        assert ch.tvg_logo == ""
        assert ch.group == ""

    def test_immutability(self) -> None:
        """S3: Channel is immutable."""
        ch = Channel(url="http://stream.example.com/live", name="My Channel")
        with pytest.raises((AttributeError, TypeError)):
            ch.name = "new name"  # type: ignore[misc]
