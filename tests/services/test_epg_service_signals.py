from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

from src.models.programme import EpgChannel, Programme
from src.services.epg_service import EpgService


class TestEpgServiceSignals:
    def test_epg_ready_emitted_after_load(self, qtbot: Any, tmp_path: Path) -> None:
        service = EpgService(cache_dir=tmp_path, refresh_hours=24)
        with patch("src.services.epg_service.parse_xmltv_url") as mock_fetch:
            mock_fetch.return_value = (
                [EpgChannel(id="ch1", names=["Ch1"])],
                [Programme(channel="ch1", title="News", start="20260101000000 +0000", stop="20260101010000 +0000")],
            )
            with qtbot.waitSignal(service.epg_ready, timeout=2000):
                service.start("https://example.com/epg.xml")

    def test_epg_error_emitted_on_fetch_failure(self, qtbot: Any, tmp_path: Path) -> None:
        service = EpgService(cache_dir=tmp_path, refresh_hours=24)
        with patch("src.services.epg_service.parse_xmltv_url") as mock_fetch:
            mock_fetch.side_effect = Exception("network failure")
            with qtbot.waitSignal(service.epg_error, timeout=2000):
                service.start("https://example.com/epg.xml")

    def test_epg_ready_on_empty_url(self, qtbot: Any, tmp_path: Path) -> None:
        service = EpgService(cache_dir=tmp_path, refresh_hours=24)
        with qtbot.waitSignal(service.epg_ready, timeout=2000):
            service.start("")
