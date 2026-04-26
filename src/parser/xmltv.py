from __future__ import annotations

import gzip
import io
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections.abc import Iterable
from pathlib import Path

from src.models.programme import EpgChannel, Programme


class XmltvParseError(Exception):
    """Raised when XMLTV content cannot be parsed."""


def _is_gzip_path(content: str) -> bool:
    return content.strip().endswith(".gz") and len(content.strip().splitlines()) == 1


def _decompress_if_gzip(content: str) -> str:
    if _is_gzip_path(content):
        path = Path(content.strip())
        if path.exists():
            with gzip.open(path, "rt", encoding="utf-8") as f:
                return f.read()
    # Check if content itself is gzip bytes encoded as latin-1 (binary in string)
    try:
        raw = content.encode("latin-1")
        if raw[:2] == b"\x1f\x8b":
            return gzip.decompress(raw).decode("utf-8")
    except Exception:
        pass
    return content


def parse_xmltv(content: str) -> tuple[list[EpgChannel], list[Programme]]:
    """Parse XMLTV-format EPG data using streaming iterparse.

    Accepts raw XML string, a path to a .gz file, or gzip-compressed bytes.
    Returns a tuple of (channels, programmes). Invalid elements are skipped.
    """
    if not content or not content.strip():
        raise XmltvParseError("Empty content")

    xml_content = _decompress_if_gzip(content)

    if not xml_content or not xml_content.strip():
        raise XmltvParseError("Empty content after decompression")

    channels: list[EpgChannel] = []
    programmes: list[Programme] = []

    try:
        context: Iterable[tuple[str, ET.Element]] = ET.iterparse(
            io.BytesIO(xml_content.encode("utf-8")), events=("start", "end")
        )
        event: str
        elem: ET.Element
        for event, elem in context:
            if event == "end":
                tag = elem.tag
                if tag == "channel":
                    ch = _parse_channel(elem)
                    if ch is not None:
                        channels.append(ch)
                    elem.clear()
                elif tag == "programme":
                    prog = _parse_programme(elem)
                    if prog is not None:
                        programmes.append(prog)
                    elem.clear()
    except ET.ParseError as exc:
        raise XmltvParseError(f"Invalid XML: {exc}") from exc
    except Exception as exc:
        raise XmltvParseError(f"Parse failed: {exc}") from exc

    return channels, programmes


def _parse_channel(elem: ET.Element) -> EpgChannel | None:
    ch_id = elem.get("id")
    if not ch_id:
        return None
    names: list[str] = []
    icon = ""
    for child in elem:
        if child.tag == "display-name" and child.text:
            names.append(child.text)
        elif child.tag == "icon":
            src = child.get("src")
            if src:
                icon = src
    return EpgChannel(id=ch_id, names=names, icon=icon)


def _parse_programme(elem: ET.Element) -> Programme | None:
    start = elem.get("start")
    stop = elem.get("stop")
    channel = elem.get("channel")
    if not start or not stop or not channel:
        return None
    title = ""
    description = ""
    category = ""
    icon = ""
    for child in elem:
        if child.tag == "title" and child.text:
            title = child.text
        elif child.tag == "desc" and child.text:
            description = child.text
        elif child.tag == "category" and child.text:
            category = child.text
        elif child.tag == "icon":
            src = child.get("src")
            if src:
                icon = src
    return Programme(
        channel=channel,
        title=title,
        start=start,
        stop=stop,
        description=description,
        category=category,
        icon=icon,
    )


def parse_xmltv_url(url: str) -> tuple[list[EpgChannel], list[Programme]]:
    """Fetch XMLTV content from a URL and parse it.

    Raises XmltvParseError on HTTP or parse failure.
    """
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            content = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise XmltvParseError(f"HTTP error {exc.code}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise XmltvParseError(f"URL error: {exc.reason}") from exc
    except Exception as exc:
        raise XmltvParseError(f"Fetch failed: {exc}") from exc

    return parse_xmltv(content)
