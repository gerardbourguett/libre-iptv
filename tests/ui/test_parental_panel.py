from __future__ import annotations

from pathlib import Path

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QLineEdit, QListWidget, QPushButton

from src.i18n import init_translator
from src.models.channel import Channel
from src.profiles.manager import ProfileManager
from src.ui.parental_panel import ParentalControlsPanel


@pytest.fixture(autouse=True)
def translator(qapp):
    init_translator(locales_dir=None)


@pytest.fixture
def tmp_manager(tmp_path: Path) -> ProfileManager:
    return ProfileManager(base_dir=tmp_path)


@pytest.fixture
def sample_channels() -> list[Channel]:
    return [
        Channel(url="http://cnn.com", name="CNN", group="News"),
        Channel(url="http://bbc.com", name="BBC", group="News"),
        Channel(url="http://espn.com", name="ESPN", group="Sports"),
    ]


@pytest.fixture
def panel(qtbot, tmp_manager, sample_channels):
    tmp_manager.create_profile("A", "#00bcd4")
    p = ParentalControlsPanel(manager=tmp_manager, channels=sample_channels)
    qtbot.addWidget(p)
    return p


class TestParentalPanelStructure:
    def test_has_pin_section(self, panel):
        texts = [w.text() for w in panel.findChildren(QPushButton)]
        texts += [w.text() for w in panel.findChildren(QLabel)]
        assert any("PIN" in t or "pin" in t.lower() for t in texts)

    def test_has_group_list(self, panel):
        lists = panel.findChildren(QListWidget)
        assert len(lists) >= 1

    def test_has_channel_list(self, panel):
        lists = panel.findChildren(QListWidget)
        assert len(lists) >= 1

    def test_spanish_labels(self, panel):
        forbidden = {"Enter", "OK", "Submit", "Save", "Delete", "Add", "Remove"}
        for widget in panel.findChildren((QPushButton, QLineEdit)):
            text = (
                widget.text()
                if hasattr(widget, "text")
                else widget.placeholderText()
            )
            for word in forbidden:
                assert word.lower() not in text.lower(), (
                    f"Found English word '{word}' in '{text}'"
                )


class TestParentalPanelGroups:
    def test_groups_populated(self, panel):
        group_list = panel._group_list
        items = [group_list.item(i).text() for i in range(group_list.count())]
        assert "News" in items
        assert "Sports" in items

    def test_check_group_emits_blocks_changed(self, panel, qtbot):
        group_list = panel._group_list
        item = group_list.item(0)
        rect = group_list.visualItemRect(item)
        with qtbot.waitSignal(panel.blocks_changed, timeout=1000):
            qtbot.mouseClick(
                group_list.viewport(),
                Qt.MouseButton.LeftButton,
                pos=rect.center(),
            )


class TestParentalPanelChannels:
    def test_channels_populated(self, panel):
        channel_list = panel._channel_list
        items = [channel_list.item(i).text() for i in range(channel_list.count())]
        assert "CNN" in items
        assert "ESPN" in items

    def test_block_channel_emits_blocks_changed(self, panel, qtbot):
        with qtbot.waitSignal(panel.blocks_changed, timeout=1000):
            panel._block_channel_at_index(0)


class TestParentalPanelPin:
    def test_set_pin_flow(self, panel, qtbot):
        # Enter new PIN and confirm
        new_pin = panel.findChild(QLineEdit, "new_pin")
        confirm_pin = panel.findChild(QLineEdit, "confirm_pin")
        if new_pin is None or confirm_pin is None:
            pytest.skip("Inline PIN form not found")
        new_pin.setText("1234")
        confirm_pin.setText("1234")
        save_btn = _find_button(panel, "Guardar")
        with qtbot.waitSignal(panel.pin_changed, timeout=1000):
            qtbot.mouseClick(save_btn, Qt.MouseButton.LeftButton)
        assert panel._manager.active_profile().pin_hash != ""

    def test_wrong_confirmation_shows_error(self, panel, qtbot):
        new_pin = panel.findChild(QLineEdit, "new_pin")
        confirm_pin = panel.findChild(QLineEdit, "confirm_pin")
        if new_pin is None or confirm_pin is None:
            pytest.skip("Inline PIN form not found")
        new_pin.setText("1234")
        confirm_pin.setText("5678")
        save_btn = _find_button(panel, "Guardar")
        qtbot.mouseClick(save_btn, Qt.MouseButton.LeftButton)
        assert "coinciden" in panel._error_label.text().lower()

    def test_remove_pin_clears_hash(self, panel, qtbot, tmp_manager):
        tmp_manager.set_pin("1234")
        panel.refresh()
        remove_btn = _find_button(panel, "Eliminar")
        panel._current_pin.setText("1234")
        received: list = []
        panel.pin_changed.connect(lambda: received.append(True))
        remove_btn.clicked.emit()
        assert received
        assert panel._manager.active_profile().pin_hash == ""


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _find_button(panel, text: str):
    for btn in panel.findChildren(QPushButton):
        if btn.text() == text:
            return btn
    pytest.fail(f"Button '{text}' not found")
