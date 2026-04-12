from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.parser.m3u import parse_m3u, parse_m3u_file

FIXTURES = Path(__file__).parent / "fixtures"


class TestParseM3uString:
    def test_valid_playlist_returns_all_channels(self) -> None:
        """S1: 3 channels from valid M3U."""
        content = (FIXTURES / "valid.m3u").read_text(encoding="utf-8")
        channels = parse_m3u(content)
        assert len(channels) == 3

    def test_full_attributes_parsed(self) -> None:
        """S2: All EXTINF attributes extracted correctly."""
        content = (
            "#EXTM3U\n"
            '#EXTINF:-1 tvg-id="cnn" tvg-name="CNN" tvg-logo="http://logo/cnn.png"'
            ' group-title="News",CNN International\n'
            "http://stream.example.com/cnn\n"
        )
        channels = parse_m3u(content)
        assert len(channels) == 1
        ch = channels[0]
        assert ch.tvg_id == "cnn"
        assert ch.tvg_name == "CNN"
        assert ch.tvg_logo == "http://logo/cnn.png"
        assert ch.group == "News"
        assert ch.name == "CNN International"
        assert ch.url == "http://stream.example.com/cnn"

    def test_missing_optional_attributes(self) -> None:
        """S3: Missing attributes default to empty string."""
        content = "#EXTINF:-1,Simple Channel\nrtsp://stream.example.com/simple\n"
        channels = parse_m3u(content)
        assert len(channels) == 1
        ch = channels[0]
        assert ch.name == "Simple Channel"
        assert ch.url == "rtsp://stream.example.com/simple"
        assert ch.tvg_id == ""
        assert ch.tvg_name == ""
        assert ch.tvg_logo == ""
        assert ch.group == ""

    def test_no_extm3u_header(self) -> None:
        """S4: Header is optional."""
        content = (FIXTURES / "no_header.m3u").read_text(encoding="utf-8")
        channels = parse_m3u(content)
        assert len(channels) == 2

    def test_empty_string(self) -> None:
        """S5: Empty string returns empty list."""
        assert parse_m3u("") == []

    def test_malformed_entry_skipped(self) -> None:
        """S6: Malformed entries skipped, valid ones returned."""
        content = (FIXTURES / "malformed.m3u").read_text(encoding="utf-8")
        channels = parse_m3u(content)
        assert len(channels) == 2
        assert channels[0].name == "Good Channel"
        assert channels[1].name == "Another Good Channel"

    def test_blank_lines_ignored(self) -> None:
        """S7: Blank lines between entries handled."""
        content = (
            "#EXTM3U\n\n"
            "#EXTINF:-1,Channel A\n\n"
            "http://stream.example.com/a\n\n"
            "#EXTINF:-1,Channel B\n\n"
            "http://stream.example.com/b\n"
        )
        channels = parse_m3u(content)
        assert len(channels) == 2

    def test_url_with_query_params(self) -> None:
        """S8: URLs with query parameters preserved."""
        url = "http://stream.example.com/live?token=abc123&quality=hd"
        content = f"#EXTINF:-1,HD Channel\n{url}\n"
        channels = parse_m3u(content)
        assert channels[0].url == url


class TestParseM3uUrl:
    def _mock_response(self, content: str):
        from unittest.mock import MagicMock
        mock = MagicMock()
        mock.read.return_value = content.encode("utf-8")
        mock.__enter__ = lambda s: s
        mock.__exit__ = MagicMock(return_value=False)
        return mock

    def test_parse_m3u_url_sends_user_agent(self):
        """parse_m3u_url must include a User-Agent header to avoid 403s."""
        from urllib.request import Request
        m3u = "#EXTM3U\n#EXTINF:-1,Test\nhttp://test\n"
        with patch("urllib.request.urlopen", return_value=self._mock_response(m3u)) as mock_open:
            from src.parser.m3u import parse_m3u_url
            parse_m3u_url("http://example.com/playlist.m3u")
        request = mock_open.call_args[0][0]
        assert isinstance(request, Request)
        assert request.get_header("User-agent") is not None

    def test_parse_m3u_url_uses_timeout(self):
        """parse_m3u_url must pass a timeout to urlopen."""
        m3u = "#EXTM3U\n#EXTINF:-1,Test\nhttp://test\n"
        with patch("urllib.request.urlopen", return_value=self._mock_response(m3u)) as mock_open:
            from src.parser.m3u import parse_m3u_url
            parse_m3u_url("http://example.com/playlist.m3u")
        call_kwargs = mock_open.call_args[1]
        assert call_kwargs.get("timeout") is not None

    def test_parse_m3u_url_fetches_and_parses(self):
        m3u_content = "#EXTM3U\n#EXTINF:-1,Test Channel\nhttp://stream.test/live\n"
        mock_response = MagicMock()
        mock_response.read.return_value = m3u_content.encode("utf-8")
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            from src.parser.m3u import parse_m3u_url
            channels = parse_m3u_url("http://example.com/playlist.m3u")

        assert len(channels) == 1
        assert channels[0].name == "Test Channel"
        assert channels[0].url == "http://stream.test/live"

    def test_parse_m3u_url_raises_on_network_error(self):
        with patch("urllib.request.urlopen", side_effect=OSError("Network error")):
            from src.parser.m3u import parse_m3u_url
            with pytest.raises(OSError):
                parse_m3u_url("http://bad.example.com/playlist.m3u")


class TestDeriveM3uPlusUrl:
    def test_path_ending_with_m3u_becomes_m3u_plus(self):
        from src.parser.m3u import _derive_m3u_plus_url
        url = "https://server.com/playlist/user/pass/m3u"
        assert _derive_m3u_plus_url(url) == "https://server.com/playlist/user/pass/m3u_plus"

    def test_path_with_query_string_preserved(self):
        from src.parser.m3u import _derive_m3u_plus_url
        url = "https://server.com/playlist/user/pass/m3u?output=hls"
        result = _derive_m3u_plus_url(url)
        assert result is not None
        assert "/m3u_plus" in result

    def test_type_m3u_query_param_upgraded(self):
        from src.parser.m3u import _derive_m3u_plus_url
        url = "https://server.com/get.php?username=X&password=Y&type=m3u"
        result = _derive_m3u_plus_url(url)
        assert result is not None
        assert "type=m3u_plus" in result

    def test_already_m3u_plus_returns_none(self):
        from src.parser.m3u import _derive_m3u_plus_url
        assert _derive_m3u_plus_url("https://server.com/playlist/u/p/m3u_plus") is None

    def test_unrecognized_pattern_returns_none(self):
        from src.parser.m3u import _derive_m3u_plus_url
        assert _derive_m3u_plus_url("https://server.com/playlist.m3u") is None


class TestFetchBestPlaylist:
    def _resp(self, content: str):
        mock = MagicMock()
        mock.read.return_value = content.encode("utf-8")
        mock.__enter__ = lambda s: s
        mock.__exit__ = MagicMock(return_value=False)
        return mock

    def test_returns_original_when_groups_already_present(self):
        """If original URL already has groups, no upgrade is attempted."""
        content = '#EXTM3U\n#EXTINF:-1 group-title="News",CNN\nhttp://cnn.com\n'
        with patch("urllib.request.urlopen", return_value=self._resp(content)) as mo:
            from src.parser.m3u import fetch_best_playlist
            channels = fetch_best_playlist("https://server.com/playlist/u/p/m3u")
        assert channels[0].group == "News"
        assert mo.call_count == 1  # Only one request made

    def test_auto_upgrades_to_m3u_plus_when_no_groups(self):
        """If original has no groups, silently retries with m3u_plus."""
        plain = "#EXTM3U\n#EXTINF:-1,TVN\nhttp://tvn.com\n"
        plus = '#EXTM3U\n#EXTINF:-1 group-title="NACIONALES",TVN\nhttp://tvn.com\n'
        with patch("urllib.request.urlopen", side_effect=[self._resp(plain), self._resp(plus)]):
            from src.parser.m3u import fetch_best_playlist
            channels = fetch_best_playlist("https://server.com/playlist/u/p/m3u")
        assert channels[0].group == "NACIONALES"

    def test_falls_back_to_original_when_plus_fails(self):
        """If m3u_plus request raises, original channels are returned silently."""
        plain = "#EXTM3U\n#EXTINF:-1,TVN\nhttp://tvn.com\n"
        with patch("urllib.request.urlopen",
                   side_effect=[self._resp(plain), OSError("404")]):
            from src.parser.m3u import fetch_best_playlist
            channels = fetch_best_playlist("https://server.com/playlist/u/p/m3u")
        assert len(channels) == 1
        assert channels[0].name == "TVN"

    def test_no_upgrade_when_url_has_no_m3u_pattern(self):
        """Unrecognized URL with no groups: original returned, no second request."""
        plain = "#EXTM3U\n#EXTINF:-1,TVN\nhttp://tvn.com\n"
        with patch("urllib.request.urlopen", return_value=self._resp(plain)) as mo:
            from src.parser.m3u import fetch_best_playlist
            channels = fetch_best_playlist("https://server.com/playlist.m3u")
        assert len(channels) == 1
        assert mo.call_count == 1


class TestParseM3uFile:
    def test_valid_file(self) -> None:
        """S1: Parse existing valid M3U file."""
        channels = parse_m3u_file(FIXTURES / "valid.m3u")
        assert len(channels) == 3

    def test_file_not_found(self) -> None:
        """S2: FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            parse_m3u_file("/nonexistent/path/playlist.m3u")

    def test_accepts_str_and_path(self) -> None:
        """S3: Both str and Path inputs work identically."""
        path = FIXTURES / "valid.m3u"
        from_path = parse_m3u_file(path)
        from_str = parse_m3u_file(str(path))
        assert from_path == from_str

    def test_utf8_encoding(self) -> None:
        """S4: UTF-8 channel names decoded correctly."""
        content = "#EXTINF:-1,Türkçe Kanal\nhttp://stream.example.com/tr\n"
        tmp = FIXTURES / "utf8_test.m3u"
        tmp.write_text(content, encoding="utf-8")
        try:
            channels = parse_m3u_file(tmp)
            assert channels[0].name == "Türkçe Kanal"
        finally:
            tmp.unlink()
