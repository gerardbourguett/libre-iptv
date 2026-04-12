from __future__ import annotations

import json
import uuid
from pathlib import Path

from src.models.profile import Profile

_INDEX_FILE = "index.json"
_MAX_RECENT = 20


class ProfileManager:
    """Manages user profiles persisted as JSON files in a directory."""

    def __init__(self, base_dir: Path | None = None) -> None:
        if base_dir is None:
            base_dir = Path.home() / ".config" / "iptv-player" / "profiles"
        self._dir = base_dir
        self._dir.mkdir(parents=True, exist_ok=True)
        self._profiles: dict[str, Profile] = {}
        self._active_id: str = ""
        self._load_index()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def needs_welcome(self) -> bool:
        """True when no profiles exist yet."""
        return len(self._profiles) == 0

    def create_profile(self, name: str, color: str) -> Profile:
        profile_id = str(uuid.uuid4())
        profile = Profile(id=profile_id, name=name, color=color)
        self._profiles[profile_id] = profile
        if not self._active_id:
            self._active_id = profile_id
        self._write_profile(profile)
        self._write_index()
        return profile

    def list_profiles(self) -> list[Profile]:
        return sorted(self._profiles.values(), key=lambda p: p.name)

    def active_profile(self) -> Profile:
        return self._profiles[self._active_id]

    def switch_profile(self, profile_id: str) -> Profile:
        if profile_id not in self._profiles:
            raise KeyError(f"Profile not found: {profile_id}")
        self.save_active()
        self._active_id = profile_id
        self._write_index()
        return self._profiles[profile_id]

    def save_active(self) -> None:
        if not self._active_id:
            return
        self._write_profile(self._profiles[self._active_id])

    def delete_profile(self, profile_id: str) -> None:
        if len(self._profiles) <= 1:
            raise ValueError("Cannot delete the only profile")
        profile_file = self._dir / f"{profile_id}.json"
        if profile_file.exists():
            profile_file.unlink()
        del self._profiles[profile_id]
        if self._active_id == profile_id:
            self._active_id = next(iter(self._profiles))
        self._write_index()

    def add_to_recent(self, channel_url: str) -> None:
        profile = self._profiles[self._active_id]
        recent = [u for u in profile.recent if u != channel_url]
        recent.insert(0, channel_url)
        self._profiles[self._active_id] = Profile(
            id=profile.id,
            name=profile.name,
            color=profile.color,
            playlist_url=profile.playlist_url,
            playlist_path=profile.playlist_path,
            favorites=profile.favorites,
            recent=recent[:_MAX_RECENT],
            last_channel_url=channel_url,
        )

    def toggle_favorite(self, channel_url: str) -> bool:
        profile = self._profiles[self._active_id]
        if channel_url in profile.favorites:
            favorites = [u for u in profile.favorites if u != channel_url]
            added = False
        else:
            favorites = [*profile.favorites, channel_url]
            added = True
        self._profiles[self._active_id] = Profile(
            id=profile.id,
            name=profile.name,
            color=profile.color,
            playlist_url=profile.playlist_url,
            playlist_path=profile.playlist_path,
            favorites=favorites,
            recent=profile.recent,
            last_channel_url=profile.last_channel_url,
        )
        return added

    def update_playlist(
        self, *, url: str = "", path: str = "", profile_id: str | None = None
    ) -> None:
        pid = profile_id or self._active_id
        profile = self._profiles[pid]
        self._profiles[pid] = Profile(
            id=profile.id,
            name=profile.name,
            color=profile.color,
            playlist_url=url,
            playlist_path=path,
            favorites=profile.favorites,
            recent=profile.recent,
            last_channel_url=profile.last_channel_url,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_index(self) -> None:
        index_path = self._dir / _INDEX_FILE
        if not index_path.exists():
            return
        data = json.loads(index_path.read_text(encoding="utf-8"))
        profile_ids: list[str] = data.get("profiles", [])
        for pid in profile_ids:
            profile_path = self._dir / f"{pid}.json"
            if profile_path.exists():
                pdata = json.loads(profile_path.read_text(encoding="utf-8"))
                self._profiles[pid] = Profile.from_dict(pdata)
        self._active_id = str(data.get("active", ""))
        if self._active_id not in self._profiles and self._profiles:
            self._active_id = next(iter(self._profiles))

    def _write_index(self) -> None:
        index = {
            "active": self._active_id,
            "profiles": list(self._profiles.keys()),
        }
        (self._dir / _INDEX_FILE).write_text(
            json.dumps(index, indent=2), encoding="utf-8"
        )

    def _write_profile(self, profile: Profile) -> None:
        (self._dir / f"{profile.id}.json").write_text(
            json.dumps(profile.to_dict(), indent=2), encoding="utf-8"
        )
