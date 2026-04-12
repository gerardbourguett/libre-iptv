import logging
import re
import urllib.request
from pathlib import Path

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
        # Next non-blank line must be the URL — stop if another directive found
        url = ""
        j = i + 1
        if j < len(lines) and not lines[j].startswith("#"):
            url = lines[j]

        if not url:
            logger.warning("Skipping #EXTINF with no URL: %s", extinf_line)
            i += 1
            continue

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


def parse_m3u_file(path: str | Path) -> list[Channel]:
    """Read an M3U file from disk and return a list of Channel instances."""
    content = Path(path).read_text(encoding="utf-8")
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
