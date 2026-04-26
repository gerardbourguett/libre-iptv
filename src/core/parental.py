from __future__ import annotations

import hashlib
import secrets
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.channel import Channel
    from src.models.profile import Profile


def hash_pin(pin: str, salt: str | None = None) -> str:
    """Return 'salt$sha256hex'. Generates a random salt if not provided."""
    if salt is None:
        salt = secrets.token_hex(8)
    digest = hashlib.sha256(f"{salt}{pin}".encode()).hexdigest()
    return f"{salt}${digest}"


def verify_pin(pin: str, stored_hash: str) -> bool:
    """Verify a 4-digit PIN against a stored salted hash."""
    if not stored_hash or "$" not in stored_hash:
        return False
    salt, _ = stored_hash.split("$", 1)
    return hash_pin(pin, salt=salt) == stored_hash


def is_channel_blocked(channel: Channel, profile: Profile) -> bool:
    """Return True if the channel URL or its group is in the profile blocklist."""
    blocked = profile.blocked if hasattr(profile, "blocked") else {}
    blocked_urls = blocked.get("channels", [])
    blocked_groups = blocked.get("groups", [])
    return channel.url in blocked_urls or channel.group in blocked_groups


def get_blocked_sets(profile: Profile) -> tuple[frozenset[str], frozenset[str]]:
    """Return (blocked_urls, blocked_groups) as frozensets for fast lookup."""
    blocked = profile.blocked if hasattr(profile, "blocked") else {}
    urls = frozenset(blocked.get("channels", []))
    groups = frozenset(blocked.get("groups", []))
    return urls, groups
