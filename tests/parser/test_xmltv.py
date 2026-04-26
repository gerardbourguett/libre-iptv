from __future__ import annotations

from pathlib import Path

import pytest

from src.models.programme import EpgChannel, Programme
from src.parser.xmltv import parse_xmltv, XmltvParseError


_VALID_XMLTV = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE tv SYSTEM "xmltv.dtd">
<tv generator-info-name="Test">
  <channel id="bbc1">
    <display-name>BBC One</display-name>
    <icon src="http://example.com/bbc1.png"/>
  </channel>
  <channel id="cnn">
    <display-name>CNN</display-name>
    <display-name>Cable News Network</display-name>
  </channel>
  <programme start="20260425143000 +0000" stop="20260425150000 +0000" channel="bbc1">
    <title>News at One</title>
    <desc>Midday news</desc>
  </programme>
  <programme start="20260425150000 +0000" stop="20260425153000 +0000" channel="bbc1">
    <title>Weather</title>
  </programme>
  <programme start="20260425140000 +0000" stop="20260425150000 +0000" channel="cnn">
    <title>CNN Newsroom</title>
    <desc>Live coverage</desc>
  </programme>
</tv>
"""


class TestParseXmltvValid:
    def test_extracts_channels(self) -> None:
        channels, programmes = parse_xmltv(_VALID_XMLTV)
        assert len(channels) == 2
        ids = {ch.id for ch in channels}
        assert ids == {"bbc1", "cnn"}

    def test_channel_fields(self) -> None:
        channels, _ = parse_xmltv(_VALID_XMLTV)
        by_id = {ch.id: ch for ch in channels}
        assert by_id["bbc1"].names == ["BBC One"]
        assert by_id["bbc1"].icon == "http://example.com/bbc1.png"
        assert by_id["cnn"].names == ["CNN", "Cable News Network"]
        assert by_id["cnn"].icon == ""

    def test_extracts_programmes(self) -> None:
        _, programmes = parse_xmltv(_VALID_XMLTV)
        assert len(programmes) == 3

    def test_programme_fields(self) -> None:
        _, programmes = parse_xmltv(_VALID_XMLTV)
        by_ch = {p.channel: p for p in programmes if p.title == "News at One"}
        assert "bbc1" in by_ch
        p = by_ch["bbc1"]
        assert p.start == "20260425143000 +0000"
        assert p.stop == "20260425150000 +0000"
        assert p.description == "Midday news"

    def test_programme_without_description_defaults_empty(self) -> None:
        _, programmes = parse_xmltv(_VALID_XMLTV)
        weather = [p for p in programmes if p.title == "Weather"]
        assert len(weather) == 1
        assert weather[0].description == ""


class TestParseXmltvMalformed:
    def test_skips_programme_missing_start(self) -> None:
        xml = """<?xml version="1.0"?>
<tv>
  <channel id="ch1"><display-name>Ch1</display-name></channel>
  <programme stop="20260425150000 +0000" channel="ch1">
    <title>Bad</title>
  </programme>
  <programme start="20260425150000 +0000" stop="20260425160000 +0000" channel="ch1">
    <title>Good</title>
  </programme>
</tv>
"""
        channels, programmes = parse_xmltv(xml)
        assert len(channels) == 1
        assert len(programmes) == 1
        assert programmes[0].title == "Good"

    def test_skips_programme_missing_stop(self) -> None:
        xml = """<?xml version="1.0"?>
<tv>
  <channel id="ch1"><display-name>Ch1</display-name></channel>
  <programme start="20260425150000 +0000" channel="ch1">
    <title>Bad</title>
  </programme>
</tv>
"""
        _, programmes = parse_xmltv(xml)
        assert len(programmes) == 0

    def test_skips_programme_missing_channel(self) -> None:
        xml = """<?xml version="1.0"?>
<tv>
  <channel id="ch1"><display-name>Ch1</display-name></channel>
  <programme start="20260425150000 +0000" stop="20260425160000 +0000">
    <title>Bad</title>
  </programme>
</tv>
"""
        _, programmes = parse_xmltv(xml)
        assert len(programmes) == 0


class TestParseXmltvEdgeCases:
    def test_empty_tv_returns_empty_lists(self) -> None:
        xml = '<?xml version="1.0"?><tv></tv>'
        channels, programmes = parse_xmltv(xml)
        assert channels == []
        assert programmes == []

    def test_empty_string_raises(self) -> None:
        with pytest.raises(XmltvParseError):
            parse_xmltv("")

    def test_invalid_xml_raises(self) -> None:
        with pytest.raises(XmltvParseError):
            parse_xmltv("not xml")


class TestParseXmltvGzip:
    def test_gzip_file_decompression(self, tmp_path: Path) -> None:
        import gzip
        xml = '<?xml version="1.0"?><tv><channel id="ch1"><display-name>Ch1</display-name></channel></tv>'
        gz_path = tmp_path / "epg.xml.gz"
        gz_path.write_bytes(gzip.compress(xml.encode("utf-8")))
        channels, programmes = parse_xmltv(str(gz_path))
        assert len(channels) == 1
        assert channels[0].id == "ch1"


class TestParseXmltvCategoryIcon:
    def test_programme_category_and_icon_extracted(self) -> None:
        xml = """<?xml version="1.0"?>
<tv>
  <channel id="ch1"><display-name>Ch1</display-name></channel>
  <programme start="20260425150000 +0000" stop="20260425160000 +0000" channel="ch1">
    <title>Sports</title>
    <category lang="es">Deportes</category>
    <icon src="http://x.com/img.png"/>
  </programme>
</tv>
"""
        _, programmes = parse_xmltv(xml)
        assert len(programmes) == 1
        assert programmes[0].category == "Deportes"
        assert programmes[0].icon == "http://x.com/img.png"

    def test_programme_missing_category_and_icon_defaults_empty(self) -> None:
        xml = """<?xml version="1.0"?>
<tv>
  <channel id="ch1"><display-name>Ch1</display-name></channel>
  <programme start="20260425150000 +0000" stop="20260425160000 +0000" channel="ch1">
    <title>News</title>
  </programme>
</tv>
"""
        _, programmes = parse_xmltv(xml)
        assert len(programmes) == 1
        assert programmes[0].category == ""
        assert programmes[0].icon == ""
