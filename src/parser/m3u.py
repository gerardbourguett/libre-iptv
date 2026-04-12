import logging
import re
import urllib.request
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from src.models.channel import Channel

logger = logging.getLogger(__name__)

_ATTR_RE = re.compile(r'([\w-]+)="([^"]*)"')


def parse_m3u(content: str) -> list[Channel]:
    """Parse M3U playlist content and return a list of Channel instances."""
    channels: list[Channel] = []
    lines = [line.strip() for line in content.splitlines()]
    lines = [line for line in lines if line]  # drop blank lines

    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.startswith("#EXTINF"):
            i += 1
            continue

        extinf_line = line
        # Skip intermediate directives (#EXTGRP, #KODIPROP, #EXTVLCOPT, etc.)
        # Stop if we hit another #EXTINF (malformed entry with no URL).
        j = i + 1
        while (
            j < len(lines)
            and lines[j].startswith("#")
            and not lines[j].startswith("#EXTINF")
        ):
            j += 1

        if j >= len(lines) or lines[j].startswith("#"):
            logger.warning("Skipping #EXTINF with no URL: %s", extinf_line)
            i += 1  # retry from next line (may be another #EXTINF)
            continue

        url = lines[j]

        attrs: dict[str, str] = {
            k: v for k, v in _ATTR_RE.findall(extinf_line)
        }

        # Display name is everything after the last comma on the #EXTINF line
        comma_pos = extinf_line.rfind(",")
        name = extinf_line[comma_pos + 1:].strip() if comma_pos != -1 else ""

        channels.append(
            Channel(
                url=url,
                name=name,
                tvg_id=attrs.get("tvg-id", ""),
                tvg_name=attrs.get("tvg-name", ""),
                tvg_logo=attrs.get("tvg-logo", ""),
                group=attrs.get("group-title", ""),
            )
        )
        i = j + 1

    return channels


def _derive_m3u_plus_url(url: str) -> str | None:
    """Return an m3u_plus variant of *url*, or None if not applicable."""
    parsed = urlparse(url)

    # Pattern 1: path ends with /m3u
    if parsed.path.endswith("/m3u"):
        new_path = parsed.path[:-4] + "/m3u_plus"
        return urlunparse(parsed._replace(path=new_path))

    # Pattern 2: query param type=m3u (Xtream-Codes /get.php style)
    qs = parse_qs(parsed.query, keep_blank_values=True)
    if qs.get("type") == ["m3u"]:
        qs["type"] = ["m3u_plus"]
        new_query = urlencode(qs, doseq=True)
        return urlunparse(parsed._replace(query=new_query))

    return None


def fetch_best_playlist(url: str) -> list[Channel]:
    """Fetch an M3U playlist, auto-upgrading to m3u_plus if groups are missing."""
    channels = parse_m3u_url(url)

    if not channels:
        return channels

    with_group = sum(1 for c in channels if c.group)
    if with_group / len(channels) > 0.10:
        return channels

    plus_url = _derive_m3u_plus_url(url)
    if plus_url is None:
        return channels

    try:
        plus_channels = parse_m3u_url(plus_url)
        plus_with_group = sum(1 for c in plus_channels if c.group)
        if plus_with_group > with_group:
            logger.info("Auto-upgraded playlist to m3u_plus: %s", plus_url)
            return plus_channels
    except Exception as exc:
        logger.warning("m3u_plus upgrade failed (%s), using original", exc)

    return channels


def parse_m3u_file(path: str | Path) -> list[Channel]:
    """Read an M3U file from disk and return a list of Channel instances.

    Tries UTF-8 first; falls back to latin-1 for files from providers that
    use legacy encodings (common with Latin American IPTV services).
    """
    p = Path(path)
    try:
        content = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = p.read_text(encoding="latin-1")
    return parse_m3u(content)


_REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
}


def parse_m3u_url(url: str) -> list[Channel]:
    """Fetch an M3U playlist from a URL and parse it."""
    req = urllib.request.Request(url, headers=_REQUEST_HEADERS)
    with urllib.request.urlopen(req, timeout=15) as response:
        content = response.read().decode("utf-8")
    return parse_m3u(content)
