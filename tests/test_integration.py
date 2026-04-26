from pathlib import Path

import pytest
from PyQt6.QtCore import QSettings

from src.i18n import init_translator, t
from src.ui.app_settings import AppSettings


@pytest.fixture
def settings(tmp_path):
    ini_path = tmp_path / "test_settings.ini"
    qs = QSettings(str(ini_path), QSettings.Format.IniFormat)
    return AppSettings(settings=qs)


class TestIntegration:
    def test_init_translator_loads_saved_language(self, tmp_path, settings):
        settings.save_language("en")
        translator = init_translator(settings=settings)
        assert translator.current_language == "en"
        assert t("menu.file") == "File"

    def test_init_translator_defaults_to_spanish(self, tmp_path, settings):
        translator = init_translator(settings=settings)
        assert translator.current_language == "es"
        assert t("menu.file") == "Archivo"
