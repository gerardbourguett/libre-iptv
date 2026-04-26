import pytest

from src.i18n import init_translator, t
from src.ui.control_bar import ControlBarWidget


@pytest.fixture(autouse=True)
def translator(qapp):
    init_translator(locales_dir=None)


@pytest.fixture
def bar(qtbot):
    w = ControlBarWidget()
    qtbot.addWidget(w)
    return w


class TestControlBarInitialState:
    def test_volume_slider_initial_value_is_100(self, bar):
        assert bar.volume_slider.value() == 100

    def test_mute_button_initial_text_is_mute(self, bar):
        assert bar.mute_btn.text() == t("control.mute")

    def test_stop_button_text_is_stop(self, bar):
        assert bar.stop_btn.text() == t("control.stop")

    def test_control_bar_has_fixed_height(self, bar):
        assert bar.height() == 56

    def test_volume_slider_is_wider(self, bar):
        assert bar.volume_slider.minimumWidth() >= 150


class TestControlBarSignals:
    def test_slider_change_emits_volume_changed(self, bar, qtbot):
        with qtbot.waitSignal(bar.volume_changed, timeout=500) as blocker:
            bar.volume_slider.setValue(50)
        assert blocker.args[0] == 50

    def test_mute_button_click_emits_mute_toggled(self, bar, qtbot):
        with qtbot.waitSignal(bar.mute_toggled, timeout=500) as blocker:
            bar.mute_btn.click()
        assert isinstance(blocker.args[0], bool)

    def test_stop_button_click_emits_stop_requested(self, bar, qtbot):
        with qtbot.waitSignal(bar.stop_requested, timeout=500):
            bar.stop_btn.click()

    def test_mute_button_text_changes_to_unmute_when_clicked(self, bar):
        bar.mute_btn.click()
        assert bar.mute_btn.text() == t("control.unmute")

    def test_mute_button_text_toggles_back_to_mute_on_second_click(self, bar):
        bar.mute_btn.click()
        bar.mute_btn.click()
        assert bar.mute_btn.text() == t("control.mute")


class TestControlBarStyling:
    def test_control_bar_has_stylesheet(self, bar):
        assert len(bar.styleSheet()) > 0

    def test_stop_button_text_contains_stop_symbol(self, bar):
        assert "■" in bar.stop_btn.text()

    def test_mute_button_text_contains_muted_symbol(self, bar):
        assert "🔇" in bar.mute_btn.text()

    def test_unmute_button_text_contains_unmuted_symbol(self, bar):
        bar.mute_btn.click()
        assert "🔊" in bar.mute_btn.text()
