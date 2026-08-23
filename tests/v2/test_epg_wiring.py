from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

from main_v2 import _build_live_epg_data, _format_epg_time
from src.models.channel import Channel
from src.models.programme import EpgChannel, Programme
from src.services.epg_service import EpgService


def _ch(name: str, tvg_id: str = "") -> Channel:
    return Channel(url=f"http://example.com/{name}", name=name, tvg_id=tvg_id)


class TestFormatEpgTime:
    def test_valid_xmltv_timestamp_returns_hh_mm(self) -> None:
        assert _format_epg_time("20260101143000 +0000") == "14:30"

    def test_garbage_input_returns_empty_string(self) -> None:
        assert _format_epg_time("not-a-timestamp") == ""

    def test_empty_string_returns_empty_string(self) -> None:
        assert _format_epg_time("") == ""


class TestBuildLiveEpgData:
    def test_builds_expected_shape_and_skips_channels(
        self, qtbot: Any, tmp_path: Path
    ) -> None:
        service = EpgService(cache_dir=tmp_path, refresh_hours=24)
        with patch("src.services.epg_service.parse_xmltv_url") as mock_fetch:
            mock_fetch.return_value = (
                [EpgChannel(id="ch1", names=["Ch1"])],
                [
                    Programme(
                        channel="ch1",
                        title="News",
                        start="20000101000000 +0000",
                        stop="20991231235959 +0000",
                    )
                ],
            )
            with qtbot.waitSignal(service.epg_ready, timeout=2000):
                service.start("https://example.com/epg.xml")

        channels = [
            _ch("Channel With Now", tvg_id="ch1"),
            _ch("Channel Without Tvg Id", tvg_id=""),
            _ch("Channel With No Current Programme", tvg_id="ch-unknown"),
        ]

        data = _build_live_epg_data(channels, service)

        assert list(data.keys()) == ["ch1"]
        assert data["ch1"]["now_title"] == "News"
        assert data["ch1"]["start"] == "00:00"
        assert data["ch1"]["end"] == "23:59"
