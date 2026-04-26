import logging
from pathlib import Path
from unittest.mock import patch

import pytest
from PyQt6.QtCore import QSettings

from src.i18n.translator import Translator
from src.ui.app_settings import AppSettings


@pytest.fixture
def translator(tmp_path):
    """Translator with mock locale files for isolated testing."""
    locales_dir = tmp_path / "locales"
    locales_dir.mkdir()

    es_path = locales_dir / "es.json"
    es_path.write_text(
        '{"menu": {"file": "Archivo"}, '
        '"status": {"channels_loaded": "Se cargaron {count} canales"}, '
        '"dialog": {"confirm": "Confirmar"}}'
    )

    en_path = locales_dir / "en.json"
    en_path.write_text(
        '{"menu": {"file": "File"}, '
        '"status": {"channels_loaded": "Loaded {count} channels"}}'
    )

    return Translator(default_locale="es", locales_dir=locales_dir)


class TestTranslatorKeyResolution:
    def test_resolve_existing_key_in_active_locale(self, translator):
        translator.set_language("en")
        assert translator.t("menu.file") == "File"

    def test_resolve_key_with_interpolation(self, translator):
        translator.set_language("en")
        assert translator.t("status.channels_loaded", count=42) == "Loaded 42 channels"


class TestTranslatorFallback:
    def test_missing_key_falls_back_to_spanish_with_warning(self, translator, caplog):
        translator.set_language("en")
        with caplog.at_level(logging.WARNING):
            result = translator.t("dialog.confirm")
        assert result == "Confirmar"
        assert "dialog.confirm" in caplog.text

    def test_missing_key_in_both_locales_returns_raw_key_with_error(self, translator, caplog):
        translator.set_language("en")
        with caplog.at_level(logging.ERROR):
            result = translator.t("nonexistent.key")
        assert result == "nonexistent.key"
        assert "nonexistent.key" in caplog.text


class TestTranslatorLanguageSwitch:
    def test_set_language_emits_signal(self, translator, qtbot):
        with qtbot.waitSignal(translator.language_changed, timeout=500):
            translator.set_language("en")

    def test_set_language_changes_resolution(self, translator):
        assert translator.t("menu.file") == "Archivo"
        translator.set_language("en")
        assert translator.t("menu.file") == "File"


class TestTranslatorDefault:
    def test_default_language_is_spanish(self, translator):
        assert translator.current_language == "es"
        assert translator.t("menu.file") == "Archivo"


class TestInitTranslator:
    def test_loads_saved_language(self, tmp_path):
        ini_path = tmp_path / "settings.ini"
        qs = QSettings(str(ini_path), QSettings.Format.IniFormat)
        qs.setValue("language/code", "en")
        settings = AppSettings(settings=qs)

        with patch("src.i18n.translator.Path") as mock_path:
            mock_locales = tmp_path / "locales"
            mock_locales.mkdir()
            (mock_locales / "es.json").write_text('{"menu": {"file": "Archivo"}}')
            (mock_locales / "en.json").write_text('{"menu": {"file": "File"}}')
            mock_path.return_value = mock_locales.parent

            from src.i18n import init_translator

            # Need to control the actual locales_dir for this test
            t = init_translator(settings=settings, locales_dir=mock_locales)
            assert t.current_language == "en"

    def test_defaults_to_spanish_when_no_saved_language(self, tmp_path):
        ini_path = tmp_path / "settings.ini"
        qs = QSettings(str(ini_path), QSettings.Format.IniFormat)
        settings = AppSettings(settings=qs)

        mock_locales = tmp_path / "locales"
        mock_locales.mkdir()
        (mock_locales / "es.json").write_text('{"menu": {"file": "Archivo"}}')
        (mock_locales / "en.json").write_text('{"menu": {"file": "File"}}')

        from src.i18n import init_translator

        t = init_translator(settings=settings, locales_dir=mock_locales)
        assert t.current_language == "es"
