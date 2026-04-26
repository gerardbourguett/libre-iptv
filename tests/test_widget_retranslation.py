
import pytest

from src.i18n import get_translator, init_translator
from src.ui.pin_dialog import PinDialog


@pytest.fixture(autouse=True)
def translator(qapp, tmp_path):
    """Initialize translator before each test and reset after."""
    init_translator(locales_dir=None)
    yield
    tr = get_translator()
    if tr is not None and tr.current_language != "es":
        tr.set_language("es")


class TestWidgetRetranslation:
    def test_control_bar_retranslates_on_language_change(self, qtbot):
        from src.ui.control_bar import ControlBarWidget

        widget = ControlBarWidget()
        qtbot.addWidget(widget)

        # Default is Spanish
        assert widget.stop_btn.text() == "■ Detener"
        assert widget.volume_slider.toolTip() == "Volumen"

        # Switch to English
        tr = get_translator()
        assert tr is not None
        with qtbot.waitSignal(tr.language_changed, timeout=500):
            tr.set_language("en")

        assert widget.stop_btn.text() == "■ Stop"
        assert widget.volume_slider.toolTip() == "Volume"

    def test_mute_button_respects_state_on_retranslate(self, qtbot):
        from src.ui.control_bar import ControlBarWidget

        widget = ControlBarWidget()
        qtbot.addWidget(widget)

        # Click mute (Spanish)
        widget.mute_btn.click()
        assert widget.mute_btn.text() == "🔊 Activar sonido"

        # Switch to English
        tr = get_translator()
        assert tr is not None
        with qtbot.waitSignal(tr.language_changed, timeout=500):
            tr.set_language("en")

        assert widget.mute_btn.text() == "🔊 Unmute"


class TestNewWidgetUsesCurrentLanguage:
    def test_pin_dialog_opens_in_english_when_language_is_english(self, qtbot):
        """REQ-04: Newly opened widget uses current language."""
        tr = get_translator()
        assert tr is not None
        with qtbot.waitSignal(tr.language_changed, timeout=500):
            tr.set_language("en")

        dialog = PinDialog()
        qtbot.addWidget(dialog)

        # Window title should be in English
        assert dialog.windowTitle() == "Parental Control"

        # Prompt label should be in English
        assert dialog._prompt.text() == "Enter PIN"

        # Confirm button should be in English
        assert dialog._confirm_btn.text() == "Confirm"

        # Cancel button should be in English
        assert dialog._cancel_btn.text() == "Cancel"
