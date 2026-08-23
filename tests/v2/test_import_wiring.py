from __future__ import annotations

from urllib.parse import parse_qs, urlsplit

from main_v2 import _build_xtream_playlist_url


class TestBuildXtreamPlaylistUrl:
    def test_includes_get_php_and_m3u_plus_params(self) -> None:
        url = _build_xtream_playlist_url("http://example.com:8080", "user", "pass")
        assert url.startswith("http://example.com:8080/get.php?")
        split = urlsplit(url)
        query = parse_qs(split.query)
        assert query["type"] == ["m3u_plus"]
        assert query["output"] == ["m3u8"]
        assert query["username"] == ["user"]
        assert query["password"] == ["pass"]

    def test_strips_trailing_slash_from_server(self) -> None:
        url = _build_xtream_playlist_url("http://example.com:8080/", "user", "pass")
        assert url.startswith("http://example.com:8080/get.php?")
        split = urlsplit(url)
        assert split.path == "/get.php"

    def test_special_characters_in_credentials_survive_round_trip(self) -> None:
        server = "http://example.com:8080"
        username = "user@name"
        password = "p@ss&w0rd=1"
        url = _build_xtream_playlist_url(server, username, password)

        split = urlsplit(url)
        query = parse_qs(split.query)
        assert query["username"] == [username]
        assert query["password"] == [password]
