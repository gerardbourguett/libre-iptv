from __future__ import annotations

from typing import cast

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.i18n import get_translator, t
from src.models.channel import Channel
from src.profiles.manager import ProfileManager


class ParentalControlsPanel(QWidget):
    """Settings panel for parental controls: PIN, blocked groups, blocked channels."""

    pin_changed = pyqtSignal()
    blocks_changed = pyqtSignal()

    def __init__(
        self,
        manager: ProfileManager,
        channels: list[Channel] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._manager = manager
        self._channels = list(channels) if channels else []

        self.setStyleSheet(
            "QWidget { background: #161616; color: #e0e0e0; }"
            "QLineEdit { background: #1e1e1e; color: #e0e0e0;"
            " border: 1px solid #2a2a2a; border-radius: 6px; padding: 6px 10px; }"
            "QPushButton { background: #1e1e1e; color: #e0e0e0;"
            " border: 1px solid #2a2a2a; border-radius: 6px; padding: 6px 14px; }"
            "QPushButton:hover { background: #262626; }"
            "QListWidget { background: #1e1e1e;"
            " border: 1px solid #2a2a2a; border-radius: 6px; }"
            "QListWidget::item { padding: 6px 10px; }"
            "QListWidget::item:selected { background: #00bcd4; color: #000000; }"
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        # PIN section
        self._pin_header = QLabel(t("parental.pin_config_title"))
        self._pin_header.setStyleSheet("font-weight: bold; font-size: 15px;")
        layout.addWidget(self._pin_header)

        self._pin_form = QFormLayout()
        self._pin_form.setSpacing(8)

        self._current_pin = QLineEdit()
        self._current_pin.setObjectName("current_pin")
        self._current_pin.setEchoMode(QLineEdit.EchoMode.Password)
        self._current_pin.setPlaceholderText(t("parental.current_pin"))
        self._current_pin.setMaxLength(4)

        self._new_pin = QLineEdit()
        self._new_pin.setObjectName("new_pin")
        self._new_pin.setEchoMode(QLineEdit.EchoMode.Password)
        self._new_pin.setPlaceholderText(t("parental.new_pin"))
        self._new_pin.setMaxLength(4)

        self._confirm_pin = QLineEdit()
        self._confirm_pin.setObjectName("confirm_pin")
        self._confirm_pin.setEchoMode(QLineEdit.EchoMode.Password)
        self._confirm_pin.setPlaceholderText(t("parental.confirm_pin"))
        self._confirm_pin.setMaxLength(4)

        self._save_pin_btn = QPushButton(t("parental.save"))
        self._save_pin_btn.clicked.connect(self._on_save_pin)

        self._remove_pin_btn = QPushButton(t("parental.remove"))
        self._remove_pin_btn.clicked.connect(self._on_remove_pin)

        pin_actions = QHBoxLayout()
        pin_actions.addWidget(self._save_pin_btn)
        pin_actions.addWidget(self._remove_pin_btn)

        self._error_label = QLabel("")
        self._error_label.setStyleSheet("color: #f44336; font-size: 12px;")

        self._pin_form.addRow(self._new_pin)
        self._pin_form.addRow(self._confirm_pin)
        self._pin_form.addRow(pin_actions)
        self._pin_form.addRow(self._error_label)

        layout.addLayout(self._pin_form)

        # Groups section
        self._groups_label = QLabel(t("parental.groups"))
        layout.addWidget(self._groups_label)

        self._group_list = QListWidget()
        self._group_list.itemClicked.connect(self._on_group_clicked)
        layout.addWidget(self._group_list)

        # Channels section
        self._channels_label = QLabel(t("parental.channels"))
        layout.addWidget(self._channels_label)

        self._channel_list = QListWidget()
        self._channel_list.itemClicked.connect(self._on_channel_clicked)
        layout.addWidget(self._channel_list)

        self.refresh()

        tr = get_translator()
        if tr is not None:
            tr.language_changed.connect(self._retranslate)

    def refresh(self) -> None:
        """Refresh UI to match current profile state."""
        profile = self._manager.active_profile()
        has_pin = bool(profile.pin_hash)

        self._current_pin.setVisible(has_pin)
        self._remove_pin_btn.setVisible(has_pin)
        self._error_label.setText("")
        self._new_pin.clear()
        self._confirm_pin.clear()
        self._current_pin.clear()

        # Populate groups
        self._group_list.clear()
        groups = sorted({ch.group for ch in self._channels if ch.group})
        blocked_groups = set(profile.blocked.get("groups", []))
        for name in groups:
            item = QListWidgetItem(name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                Qt.CheckState.Checked
                if name in blocked_groups
                else Qt.CheckState.Unchecked
            )
            self._group_list.addItem(item)

        # Populate channels
        self._channel_list.clear()
        blocked_urls = set(profile.blocked.get("channels", []))
        for ch in self._channels:
            item = QListWidgetItem(ch.name)
            item.setData(Qt.ItemDataRole.UserRole, ch)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                Qt.CheckState.Checked
                if ch.url in blocked_urls
                else Qt.CheckState.Unchecked
            )
            self._channel_list.addItem(item)

    def _on_save_pin(self) -> None:
        profile = self._manager.active_profile()
        new = self._new_pin.text().strip()
        confirm = self._confirm_pin.text().strip()

        if len(new) != 4 or not new.isdigit():
            self._error_label.setText(t("parental.error.pin_digits"))
            return

        if new != confirm:
            self._error_label.setText(t("parental.error.pin_mismatch"))
            return

        if profile.pin_hash:
            current = self._current_pin.text().strip()
            if not self._manager.verify_pin(current):
                self._error_label.setText(t("parental.error.current_pin_wrong"))
                return

        self._manager.set_pin(new)
        self._error_label.setText("")
        self.refresh()
        self.pin_changed.emit()

    def _on_remove_pin(self) -> None:
        profile = self._manager.active_profile()
        if not profile.pin_hash:
            return
        current = self._current_pin.text().strip()
        if not self._manager.verify_pin(current):
            self._error_label.setText(t("parental.error.current_pin_wrong"))
            return
        self._manager.remove_pin()
        self._error_label.setText("")
        self.refresh()
        self.pin_changed.emit()

    def _retranslate(self, _code: str) -> None:
        self._pin_header.setText(t("parental.pin_config_title"))
        self._current_pin.setPlaceholderText(t("parental.current_pin"))
        self._new_pin.setPlaceholderText(t("parental.new_pin"))
        self._confirm_pin.setPlaceholderText(t("parental.confirm_pin"))
        self._save_pin_btn.setText(t("parental.save"))
        self._remove_pin_btn.setText(t("parental.remove"))
        self._groups_label.setText(t("parental.groups"))
        self._channels_label.setText(t("parental.channels"))

    def _on_group_clicked(self, item: QListWidgetItem) -> None:
        name = item.text()
        if item.checkState() == Qt.CheckState.Checked:
            self._manager.block_group(name)
        else:
            self._manager.unblock_group(name)
        self.blocks_changed.emit()

    def _on_channel_clicked(self, item: QListWidgetItem) -> None:
        ch = cast(Channel, item.data(Qt.ItemDataRole.UserRole))
        if item.checkState() == Qt.CheckState.Checked:
            self._manager.block_channel(ch.url)
        else:
            self._manager.unblock_channel(ch.url)
        self.blocks_changed.emit()

    def _block_channel_at_index(self, index: int) -> None:
        """Toggle block status for the channel at the given list index."""
        item = self._channel_list.item(index)
        if item is None:
            return
        ch = cast(Channel, item.data(Qt.ItemDataRole.UserRole))
        if ch.url in self._manager.active_profile().blocked.get("channels", []):
            self._manager.unblock_channel(ch.url)
            item.setCheckState(Qt.CheckState.Unchecked)
        else:
            self._manager.block_channel(ch.url)
            item.setCheckState(Qt.CheckState.Checked)
        self.blocks_changed.emit()
