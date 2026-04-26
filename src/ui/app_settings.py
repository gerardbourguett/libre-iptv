from PyQt6.QtCore import QByteArray, QSettings

# DEPRECATED: Replaced by src.core.settings.SettingsManager.
# Kept for one release cycle for backward compatibility.


class AppSettings:
    def __init__(self, settings: QSettings | None = None) -> None:
        if settings is not None:
            self._qs = settings
        else:
            self._qs = QSettings(
                QSettings.Format.IniFormat,
                QSettings.Scope.UserScope,
                "iptv",
                "iptv-player",
            )

    def save_geometry(self, geometry: QByteArray) -> None:
        self._qs.setValue("window/geometry", geometry)

    def load_geometry(self) -> QByteArray | None:
        value = self._qs.value("window/geometry")
        if isinstance(value, QByteArray) and not value.isEmpty():
            return value
        return None

    def save_splitter(self, sizes: list[int]) -> None:
        self._qs.setValue("window/splitter_sizes", sizes)

    def load_splitter(self) -> list[int] | None:
        value = self._qs.value("window/splitter_sizes")
        if value is None:
            return None
        # QSettings may return list of strings on some platforms
        try:
            return [int(v) for v in value]
        except (TypeError, ValueError):
            return None

    def save_last_playlist(self, path: str) -> None:
        self._qs.setValue("playlist/last_path", path)

    def load_last_playlist(self) -> str | None:
        value = self._qs.value("playlist/last_path")
        return str(value) if value is not None else None

    def save_language(self, code: str) -> None:
        self._qs.setValue("language/code", code)

    def load_language(self) -> str | None:
        value = self._qs.value("language/code")
        return str(value) if value is not None else None
