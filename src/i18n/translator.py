import json
import logging
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)


class Translator(QObject):
    language_changed = pyqtSignal(str)

    def __init__(
        self,
        default_locale: str = "es",
        locales_dir: Path | None = None,
    ) -> None:
        super().__init__()
        self._default_locale = default_locale
        self._current_locale = default_locale
        self._locales_dir = locales_dir or Path(__file__).parent / "locales"
        self._data: dict[str, dict[str, object]] = {}
        self._load_locale(default_locale)

    @property
    def current_language(self) -> str:
        return self._current_locale

    def _load_locale(self, code: str) -> None:
        path = self._locales_dir / f"{code}.json"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                self._data[code] = json.load(f)
        else:
            self._data[code] = {}

    def _resolve(self, key: str, locale: str) -> str | None:
        data: object = self._data.get(locale, {})
        parts = key.split(".")
        for part in parts:
            if isinstance(data, dict) and part in data:
                data = data[part]
            else:
                return None
        if isinstance(data, str):
            return data
        return None

    def t(self, key: str, **kwargs: object) -> str:
        value = self._resolve(key, self._current_locale)
        if value is None:
            value = self._resolve(key, self._default_locale)
            if value is not None:
                logger.warning(
                    "Missing key '%s' in locale '%s', falling back to '%s'",
                    key,
                    self._current_locale,
                    self._default_locale,
                )
            else:
                logger.error(
                    "Missing key '%s' in both locale '%s' and default '%s'",
                    key,
                    self._current_locale,
                    self._default_locale,
                )
                return key
        return value.format(**kwargs) if kwargs else value

    def set_language(self, code: str) -> None:
        if code not in self._data:
            self._load_locale(code)
        self._current_locale = code
        self.language_changed.emit(code)


def init_translator(
    settings: object | None = None,
    locales_dir: Path | None = None,
) -> Translator:
    from src.ui.app_settings import AppSettings

    app_settings = settings if isinstance(settings, AppSettings) else AppSettings()
    saved = app_settings.load_language()
    locale = saved if saved is not None else "es"
    translator = Translator(default_locale="es", locales_dir=locales_dir)
    if locale != "es":
        translator.set_language(locale)
    global _translator
    _translator = translator
    return translator


_translator: Translator | None = None


def get_translator() -> Translator | None:
    return _translator


def t(key: str, **kwargs: object) -> str:
    if _translator is None:
        raise RuntimeError("Translator not initialized. Call init_translator() first.")
    return _translator.t(key, **kwargs)
