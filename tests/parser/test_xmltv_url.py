from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.models.programme import EpgChannel, Programme
from src.parser.xmltv import parse_xmltv_url, XmltvParseError


_XMLTV_SAMPLE = """<?xml version="1.0"?>
<tv>
  <channel id="ch1"><display-name>Ch1</display-name></channel>
  <programme start="20260425143000 +0000" stop="20260425150000 +0000" channel="ch1">
    <title>News</title>
  </programme>
</tv>
"""


class TestParseXmltvUrl:
    @patch("urllib.request.urlopen")
    def test_fetch_and_parse_returns_channels_and_programmes(self, mock_urlopen: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = _XMLTV_SAMPLE.encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        channels, programmes = parse_xmltv_url("https://example.com/epg.xml")
        assert len(channels) == 1
        assert isinstance(channels[0], EpgChannel)
        assert channels[0].id == "ch1"
        assert len(programmes) == 1
        assert isinstance(programmes[0], Programme)
        assert programmes[0].title == "News"

    @patch("urllib.request.urlopen")
    def test_http_error_raises_xmltv_parse_error(self, mock_urlopen: MagicMock) -> None:
        from urllib.error import HTTPError

        mock_urlopen.side_effect = HTTPError(
            url="https://example.com/epg.xml",
            code=404,
            msg="Not Found",
            hdrs={},  # type: ignore[arg-type]
            fp=None,  # type: ignore[arg-type]
        )
        with pytest.raises(XmltvParseError) as exc_info:
            parse_xmltv_url("https://example.com/epg.xml")
        assert "404" in str(exc_info.value)

    @patch("urllib.request.urlopen")
    def test_url_error_raises_xmltv_parse_error(self, mock_urlopen: MagicMock) -> None:
        from urllib.error import URLError

        mock_urlopen.side_effect = URLError("Name or service not known")
        with pytest.raises(XmltvParseError) as exc_info:
            parse_xmltv_url("https://bad-url.test/epg.xml")
        assert "URL error" in str(exc_info.value)

    @patch("urllib.request.urlopen")
    def test_invalid_xml_from_url_raises_xmltv_parse_error(self, mock_urlopen: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = b"not xml"
        mock_urlopen.return_value.__enter__.return_value = mock_response

        with pytest.raises(XmltvParseError):
            parse_xmltv_url("https://example.com/bad.xml")
