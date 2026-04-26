from __future__ import annotations

from typing import Any

import pytest

from src.models.programme import Programme
from src.services.epg_service import EpgService


class TestEpgServiceNowNext:
    def test_unknown_tvg_id_returns_none_none(self) -> None:
        service = EpgService(cache_dir=None, refresh_hours=24)
        now, next_prog = service.get_now_next("unknown")
        assert now is None
        assert next_prog is None

    def test_now_next_for_known_channel(self, monkeypatch: Any) -> None:
        service = EpgService(cache_dir=None, refresh_hours=24)
        # Seed programmes directly
        service._programmes = {
            "bbc1": [
                Programme(channel="bbc1", title="Morning", start="20260425060000 +0000", stop="20260425070000 +0000"),
                Programme(channel="bbc1", title="News", start="20260425070000 +0000", stop="20260425080000 +0000"),
                Programme(channel="bbc1", title="Documentary", start="20260425080000 +0000", stop="20260425090000 +0000"),
            ]
        }
        # Mock current time to 07:30 UTC
        monkeypatch.setattr(
            "src.services.epg_service.time.strftime",
            lambda fmt, gm: "20260425073000 +0000" if fmt == "%Y%m%d%H%M%S %z" else "",
        )
        now, next_prog = service.get_now_next("bbc1")
        assert now is not None
        assert now.title == "News"
        assert next_prog is not None
        assert next_prog.title == "Documentary"

    def test_before_first_programme_returns_none_and_first(self, monkeypatch: Any) -> None:
        service = EpgService(cache_dir=None, refresh_hours=24)
        service._programmes = {
            "ch1": [
                Programme(channel="ch1", title="First", start="20260425100000 +0000", stop="20260425110000 +0000"),
            ]
        }
        monkeypatch.setattr(
            "src.services.epg_service.time.strftime",
            lambda fmt, gm: "20260425090000 +0000" if fmt == "%Y%m%d%H%M%S %z" else "",
        )
        now, next_prog = service.get_now_next("ch1")
        assert now is None
        assert next_prog is not None
        assert next_prog.title == "First"

    def test_after_last_programme_returns_last_and_none(self, monkeypatch: Any) -> None:
        service = EpgService(cache_dir=None, refresh_hours=24)
        service._programmes = {
            "ch1": [
                Programme(channel="ch1", title="Last", start="20260425100000 +0000", stop="20260425110000 +0000"),
            ]
        }
        monkeypatch.setattr(
            "src.services.epg_service.time.strftime",
            lambda fmt, gm: "20260425120000 +0000" if fmt == "%Y%m%d%H%M%S %z" else "",
        )
        now, next_prog = service.get_now_next("ch1")
        assert now is not None
        assert now.title == "Last"
        assert next_prog is None
