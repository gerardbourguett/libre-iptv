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


class TestChannelId:
    def test_id_is_sha256_of_url_truncated(self) -> None:
        """REQ-01: id is first 12 hex chars of SHA-256(url)."""
        import hashlib

        url = "http://ex.com/s1.ts"
        expected = hashlib.sha256(url.encode()).hexdigest()[:12]
        ch = Channel(url=url, name="Ch1")
        assert ch.id == expected

    def test_id_is_deterministic(self) -> None:
        """Same URL always produces same id."""
        ch1 = Channel(url="http://same.com/stream", name="A")
        ch2 = Channel(url="http://same.com/stream", name="B")
        assert ch1.id == ch2.id

    def test_different_urls_different_ids(self) -> None:
        """Different URLs produce different ids."""
        ch1 = Channel(url="http://a.com/1", name="A")
        ch2 = Channel(url="http://a.com/2", name="B")
        assert ch1.id != ch2.id


class TestChannelNum:
    def test_num_defaults_to_zero(self) -> None:
        """REQ-02: num defaults to 0."""
        ch = Channel(url="http://x.com", name="X")
        assert ch.num == 0

    def test_num_can_be_set(self) -> None:
        """num can be passed explicitly."""
        ch = Channel(url="http://x.com", name="X", num=42)
        assert ch.num == 42


class TestChannelContentFlags:
    def test_defaults_live_true(self) -> None:
        """REQ-03: defaults is_live=True, is_vod=False, is_series=False."""
        ch = Channel(url="http://x.com", name="X")
        assert ch.is_live is True
        assert ch.is_vod is False
        assert ch.is_series is False

    def test_flags_can_be_set(self) -> None:
        ch = Channel(url="http://x.com", name="X", is_live=False, is_vod=True, is_series=True)
        assert ch.is_live is False
        assert ch.is_vod is True
        assert ch.is_series is True


class TestChannelBackwardCompat:
    def test_construct_with_only_url_and_name(self) -> None:
        """REQ-04: Channel(url=..., name=...) still works."""
        ch = Channel(url="http://x.com", name="X")
        assert ch.url == "http://x.com"
        assert ch.name == "X"
        assert ch.id != ""
        assert ch.num == 0
        assert ch.is_live is True
        assert ch.is_vod is False
        assert ch.is_series is False

    def test_construct_with_all_old_fields(self) -> None:
        """Old positional/kwarg construction still works."""
        ch = Channel(
            url="http://x.com",
            name="X",
            tvg_id="x",
            tvg_name="X Name",
            tvg_logo="http://logo.png",
            group="News",
        )
        assert ch.tvg_id == "x"
        assert ch.tvg_name == "X Name"
        assert ch.tvg_logo == "http://logo.png"
        assert ch.group == "News"
        assert ch.id != ""
        assert ch.num == 0
        assert ch.is_live is True
