from __future__ import annotations

import pytest

from src.models.programme import EpgChannel, Programme


class TestEpgChannel:
    def test_basic_fields(self) -> None:
        ch = EpgChannel(id="bbc1", names=["BBC One"], icon="http://logo.png")
        assert ch.id == "bbc1"
        assert ch.names == ["BBC One"]
        assert ch.icon == "http://logo.png"

    def test_default_icon(self) -> None:
        ch = EpgChannel(id="cnn", names=["CNN"])
        assert ch.icon == ""

    def test_frozen(self) -> None:
        ch = EpgChannel(id="x", names=["X"])
        with pytest.raises(AttributeError):
            ch.id = "y"


class TestProgramme:
    def test_basic_fields(self) -> None:
        p = Programme(
            channel="bbc1",
            title="News",
            start="20260425143000 +0000",
            stop="20260425150000 +0000",
            description="Evening news",
        )
        assert p.channel == "bbc1"
        assert p.title == "News"
        assert p.start == "20260425143000 +0000"
        assert p.stop == "20260425150000 +0000"
        assert p.description == "Evening news"

    def test_default_description(self) -> None:
        p = Programme(
            channel="bbc1",
            title="News",
            start="20260425143000 +0000",
            stop="20260425150000 +0000",
        )
        assert p.description == ""

    def test_frozen(self) -> None:
        p = Programme(channel="x", title="T", start="20260101000000 +0000", stop="20260101010000 +0000")
        with pytest.raises(AttributeError):
            p.title = "Y"


class TestProgrammeSerialization:
    def test_to_dict(self) -> None:
        p = Programme(
            channel="bbc1",
            title="News",
            start="20260425143000 +0000",
            stop="20260425150000 +0000",
            description="Evening news",
        )
        d = p.to_dict()
        assert d == {
            "channel": "bbc1",
            "title": "News",
            "start": "20260425143000 +0000",
            "stop": "20260425150000 +0000",
            "description": "Evening news",
            "category": "",
            "icon": "",
        }

    def test_from_dict(self) -> None:
        d = {
            "channel": "cnn",
            "title": "Sports",
            "start": "20260425150000 +0000",
            "stop": "20260425160000 +0000",
            "description": "Live match",
        }
        p = Programme.from_dict(d)
        assert p.channel == "cnn"
        assert p.title == "Sports"
        assert p.start == "20260425150000 +0000"
        assert p.stop == "20260425160000 +0000"
        assert p.description == "Live match"

    def test_from_dict_missing_description(self) -> None:
        d = {
            "channel": "x",
            "title": "Y",
            "start": "20260101000000 +0000",
            "stop": "20260101010000 +0000",
        }
        p = Programme.from_dict(d)
        assert p.description == ""

    def test_roundtrip(self) -> None:
        original = Programme(
            channel="bbc2",
            title="Documentary",
            start="20260425200000 +0000",
            stop="20260425210000 +0000",
            description="Nature",
        )
        restored = Programme.from_dict(original.to_dict())
        assert restored == original

    def test_category_defaults_empty(self) -> None:
        p = Programme(channel="x", title="T", start="20260101000000 +0000", stop="20260101010000 +0000")
        assert p.category == ""

    def test_icon_defaults_empty(self) -> None:
        p = Programme(channel="x", title="T", start="20260101000000 +0000", stop="20260101010000 +0000")
        assert p.icon == ""

    def test_category_and_icon_can_be_set(self) -> None:
        p = Programme(
            channel="x",
            title="T",
            start="20260101000000 +0000",
            stop="20260101010000 +0000",
            category="Deportes",
            icon="http://x.com/img.png",
        )
        assert p.category == "Deportes"
        assert p.icon == "http://x.com/img.png"

    def test_to_dict_includes_category_and_icon(self) -> None:
        p = Programme(
            channel="x",
            title="T",
            start="20260101000000 +0000",
            stop="20260101010000 +0000",
            category="Deportes",
            icon="http://x.com/img.png",
        )
        d = p.to_dict()
        assert d["category"] == "Deportes"
        assert d["icon"] == "http://x.com/img.png"

    def test_from_dict_with_category_and_icon(self) -> None:
        d = {
            "channel": "x",
            "title": "T",
            "start": "20260101000000 +0000",
            "stop": "20260101010000 +0000",
            "category": "Deportes",
            "icon": "http://x.com/img.png",
        }
        p = Programme.from_dict(d)
        assert p.category == "Deportes"
        assert p.icon == "http://x.com/img.png"

    def test_from_dict_missing_category_and_icon_defaults_empty(self) -> None:
        d = {
            "channel": "x",
            "title": "T",
            "start": "20260101000000 +0000",
            "stop": "20260101010000 +0000",
        }
        p = Programme.from_dict(d)
        assert p.category == ""
        assert p.icon == ""

    def test_roundtrip_with_category_and_icon(self) -> None:
        original = Programme(
            channel="bbc2",
            title="Documentary",
            start="20260425200000 +0000",
            stop="20260425210000 +0000",
            description="Nature",
            category="Naturaleza",
            icon="http://x.com/nature.png",
        )
        restored = Programme.from_dict(original.to_dict())
        assert restored == original
