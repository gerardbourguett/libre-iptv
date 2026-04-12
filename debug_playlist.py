"""
Diagnostic: fetch a playlist URL and report groups + sample EXTINF lines.
Usage:
    python debug_playlist.py <url>
"""
import sys
import urllib.request
from src.parser.m3u import _REQUEST_HEADERS, parse_m3u

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python debug_playlist.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    print(f"Fetching: {url}\n")

    req = urllib.request.Request(url, headers=_REQUEST_HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read().decode("utf-8")

    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    extinf_lines = [l for l in lines if l.startswith("#EXTINF")]

    print(f"Total lines     : {len(lines)}")
    print(f"#EXTINF entries : {len(extinf_lines)}")
    print()

    # Show first 5 raw EXTINF lines so we can see attribute format
    print("=== First 5 #EXTINF lines (raw) ===")
    for line in extinf_lines[:5]:
        print(" ", line)
    print()

    # Show ALL non-EXTINF, non-URL lines (directives, EXTGRP, etc.)
    url_lines = {l for l in lines if l.startswith("http") or l.startswith("rtsp") or l.startswith("rtp")}
    other_lines = [l for l in lines if not l.startswith("#EXTINF") and l not in url_lines]
    print(f"=== Other directives / tags ({len(other_lines)}) ===")
    for line in other_lines[:30]:
        print(" ", line)
    print()

    # Parse and report groups
    channels = parse_m3u(raw)
    groups: dict[str, int] = {}
    for ch in channels:
        key = ch.group if ch.group else "(empty — goes to Uncategorized)"
        groups[key] = groups.get(key, 0) + 1

    print(f"=== Groups found ({len(groups)}) ===")
    for group, count in sorted(groups.items(), key=lambda x: -x[1]):
        print(f"  {repr(group):45s}  {count:4d} canales")

if __name__ == "__main__":
    main()
