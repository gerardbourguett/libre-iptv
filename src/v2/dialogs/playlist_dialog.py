from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)


class PlaylistDialog(QDialog):
    """Dialog to configure an M3U playlist via URL or local file."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Configurar lista M3U")
        self.setMinimumWidth(480)
        self.setModal(True)

        self._result_url: str = ""
        self._result_path: str = ""

        self._build_ui()

    # ------------------------------------------------------------------
    # Public properties
    # ------------------------------------------------------------------

    @property
    def result_url(self) -> str:
        return self._result_url

    @property
    def result_path(self) -> str:
        return self._result_path

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 20, 24, 16)

        # --- Title ---
        title = QLabel("Elegí el origen de tu lista M3U")
        title.setStyleSheet("font-size: 15px; font-weight: bold;")
        layout.addWidget(title)

        # --- Radio: URL ---
        self._radio_url = QRadioButton("URL remota (http/https)")
        self._radio_url.setChecked(True)
        layout.addWidget(self._radio_url)

        # URL input
        self._url_input = QLineEdit()
        self._url_input.setPlaceholderText("https://ejemplo.com/lista.m3u")
        self._url_input.setMinimumHeight(36)
        layout.addWidget(self._url_input)

        # --- Radio: File ---
        self._radio_file = QRadioButton("Archivo local")
        layout.addWidget(self._radio_file)

        # File picker row
        file_row = QHBoxLayout()
        self._file_label = QLabel("Ningún archivo seleccionado")
        self._file_label.setStyleSheet("color: #888888;")
        self._file_label.setEnabled(False)
        file_row.addWidget(self._file_label, stretch=1)

        self._browse_btn = QPushButton("Examinar…")
        self._browse_btn.setEnabled(False)
        self._browse_btn.clicked.connect(self._browse_file)
        file_row.addWidget(self._browse_btn)
        layout.addLayout(file_row)

        # Wire radio toggles
        self._radio_url.toggled.connect(self._on_mode_changed)
        self._radio_file.toggled.connect(self._on_mode_changed)

        # --- Buttons ---
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        ok_btn = buttons.button(QDialogButtonBox.StandardButton.Ok)
        cancel_btn = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        if ok_btn:
            ok_btn.setText("Cargar")
        if cancel_btn:
            cancel_btn.setText("Cancelar")
        layout.addWidget(buttons, alignment=Qt.AlignmentFlag.AlignRight)

    def _on_mode_changed(self) -> None:
        url_mode = self._radio_url.isChecked()
        self._url_input.setEnabled(url_mode)
        self._file_label.setEnabled(not url_mode)
        self._browse_btn.setEnabled(not url_mode)

    def _browse_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo M3U",
            "",
            "Listas M3U (*.m3u *.m3u8);;Todos los archivos (*)",
        )
        if path:
            self._file_label.setText(path)
            self._file_label.setStyleSheet("color: #e0e0e0;")

    def _on_accept(self) -> None:
        if self._radio_url.isChecked():
            url = self._url_input.text().strip()
            if not url:
                self._url_input.setFocus()
                return
            self._result_url = url
            self._result_path = ""
        else:
            path = self._file_label.text().strip()
            if path == "Ningún archivo seleccionado" or not path:
                self._browse_file()
                return
            self._result_path = path
            self._result_url = ""

        self.accept()
