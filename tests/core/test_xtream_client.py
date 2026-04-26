from __future__ import annotations

import io
import json
from unittest.mock import patch

import pytest

from src.core.xtream_client import AccountInfo, XtreamClient


@pytest.fixture
def client() -> XtreamClient:
    return XtreamClient("http://example.com:8080", "testuser", "testpass")


def _urlopen(data: bytes) -> io.BytesIO:
    return io.BytesIO(data)


class TestXtreamClientInit:
    def test_strips_trailing_slash(self) -> None:
        c = XtreamClient("http://example.com:8080/", "u", "p")
        assert c._server == "http://example.com:8080"

    def test_stores_credentials(self) -> None:
        c = XtreamClient("http://x.com", "myuser", "mypass")
        assert c._username == "myuser"
        assert c._password == "mypass"


class TestAccountInfo:
    def test_returns_account_info(self, client: XtreamClient) -> None:
        payload = {
            "user_info": {
                "status": "Active",
                "exp_date": "1893456000",
                "is_trial": "0",
                "active_cons": "1",
                "max_connections": "2",
                "allowed_output_formats": ["m3u8", "ts"],
            }
        }
        with patch("urllib.request.urlopen", return_value=_urlopen(json.dumps(payload).encode())):
            info = client.account_info()
        assert isinstance(info, AccountInfo)
        assert info.status == "Active"
        assert info.max_connections == 2
        assert not info.is_trial
        assert info.allowed_output_formats == ["m3u8", "ts"]

    def test_trial_account(self, client: XtreamClient) -> None:
        payload = {"user_info": {"status": "Active", "is_trial": "1", "max_connections": "1"}}
        with patch("urllib.request.urlopen", return_value=_urlopen(json.dumps(payload).encode())):
            info = client.account_info()
        assert info.is_trial

    def test_active_cons(self, client: XtreamClient) -> None:
        payload = {"user_info": {"active_cons": "3", "max_connections": "5"}}
        with patch("urllib.request.urlopen", return_value=_urlopen(json.dumps(payload).encode())):
            info = client.account_info()
        assert info.active_cons == 3

    def test_username_in_result(self, client: XtreamClient) -> None:
        payload: dict = {"user_info": {}}
        with patch("urllib.request.urlopen", return_value=_urlopen(json.dumps(payload).encode())):
            info = client.account_info()
        assert info.username == "testuser"
        assert info.password == "testpass"


class TestGetM3uPlus:
    def test_returns_m3u_text(self, client: XtreamClient) -> None:
        m3u = "#EXTM3U\n#EXTINF:-1,Channel\nhttp://stream.m3u8"
        with patch("urllib.request.urlopen", return_value=_urlopen(m3u.encode())):
            result = client.get_m3u_plus()
        assert result == m3u

    def test_calls_get_php(self, client: XtreamClient) -> None:
        with patch("urllib.request.urlopen", return_value=_urlopen(b"#EXTM3U")) as mock:
            client.get_m3u_plus()
        req = mock.call_args[0][0]
        assert "/get.php" in req.full_url

    def test_includes_m3u_plus_type(self, client: XtreamClient) -> None:
        with patch("urllib.request.urlopen", return_value=_urlopen(b"#EXTM3U")) as mock:
            client.get_m3u_plus()
        req = mock.call_args[0][0]
        assert "type=m3u_plus" in req.full_url


class TestGetXmltv:
    def test_returns_bytes(self, client: XtreamClient) -> None:
        content = b"<?xml version='1.0'?><tv></tv>"
        with patch("urllib.request.urlopen", return_value=_urlopen(content)):
            result = client.get_xmltv()
        assert result == content

    def test_calls_xmltv_php(self, client: XtreamClient) -> None:
        with patch("urllib.request.urlopen", return_value=_urlopen(b"")) as mock:
            client.get_xmltv()
        req = mock.call_args[0][0]
        assert "/xmltv.php" in req.full_url


class TestGetLiveCategories:
    def test_returns_list(self, client: XtreamClient) -> None:
        cats = [{"category_id": "1", "category_name": "Sports"}]
        with patch("urllib.request.urlopen", return_value=_urlopen(json.dumps(cats).encode())):
            result = client.get_live_categories()
        assert result == cats

    def test_action_param(self, client: XtreamClient) -> None:
        with patch("urllib.request.urlopen", return_value=_urlopen(b"[]")) as mock:
            client.get_live_categories()
        req = mock.call_args[0][0]
        assert "action=get_live_categories" in req.full_url

    def test_empty_response(self, client: XtreamClient) -> None:
        with patch("urllib.request.urlopen", return_value=_urlopen(b"[]")):
            result = client.get_live_categories()
        assert result == []


class TestGetVodCategories:
    def test_returns_list(self, client: XtreamClient) -> None:
        cats = [{"category_id": "2", "category_name": "Movies"}]
        with patch("urllib.request.urlopen", return_value=_urlopen(json.dumps(cats).encode())):
            result = client.get_vod_categories()
        assert result == cats

    def test_action_param(self, client: XtreamClient) -> None:
        with patch("urllib.request.urlopen", return_value=_urlopen(b"[]")) as mock:
            client.get_vod_categories()
        req = mock.call_args[0][0]
        assert "action=get_vod_categories" in req.full_url


class TestGetVodInfo:
    def test_returns_dict(self, client: XtreamClient) -> None:
        info = {"info": {"name": "Movie A", "year": "2023"}, "movie_data": {}}
        with patch("urllib.request.urlopen", return_value=_urlopen(json.dumps(info).encode())):
            result = client.get_vod_info(42)
        assert result == info

    def test_passes_vod_id(self, client: XtreamClient) -> None:
        with patch("urllib.request.urlopen", return_value=_urlopen(b"{}")) as mock:
            client.get_vod_info(99)
        req = mock.call_args[0][0]
        assert "vod_id=99" in req.full_url
        assert "action=get_vod_info" in req.full_url

    def test_accepts_string_id(self, client: XtreamClient) -> None:
        with patch("urllib.request.urlopen", return_value=_urlopen(b"{}")) as mock:
            client.get_vod_info("abc123")
        req = mock.call_args[0][0]
        assert "vod_id=abc123" in req.full_url


class TestGetStreamUrl:
    def test_returns_stream_url(self, client: XtreamClient) -> None:
        url = client.get_stream_url("TOKEN123")
        assert url == "http://example.com:8080/play/TOKEN123/m3u8"

    def test_custom_output(self, client: XtreamClient) -> None:
        url = client.get_stream_url("TOKEN123", output="ts")
        assert url == "http://example.com:8080/play/TOKEN123/ts"

    def test_no_double_slash(self) -> None:
        c = XtreamClient("http://example.com:8080/", "u", "p")
        url = c.get_stream_url("TOK")
        assert "//play" not in url
