from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

_BG = "#060810"
_SURFACE = "#0c0e18"
_ELEVATED = "#121522"
_BORDER = "rgba(255,255,255,0.06)"
_TEXT = "#e8eaf0"
_DIM = "#555761"
_SEC = "#9698a0"
_ACCENT = "#001999"

_METHODS = ["file", "url", "xtream"]

_METHOD_META = {
    "file": {
        "icon": "📁",
        "title": "Archivo M3U local",
        "desc": "Arrastrá o seleccioná un archivo .m3u / .m3u8 desde tu disco",
        "tags": ["Offline", "Privado"],
    },
    "url": {
        "icon": "🔗",
        "title": "URL de lista M3U",
        "desc": "Pegá la URL de tu proveedor IPTV. Soporta http y https.",
        "tags": ["Auto-actualiza", "Token auth"],
    },
    "xtream": {
        "icon": "⚡",
        "title": "Xtream Codes API",
        "desc": "Conectá directamente con servidor, usuario y contraseña.",
        "tags": ["EPG incluido", "VOD automático"],
    },
}

_INPUT_STYLE = (
    f"background: {_ELEVATED}; color: {_TEXT}; "
    f"border: 1px solid {_BORDER}; padding: 12px 14px; font-size: 13px;"
)


class ImportScreen(QWidget):
    import_requested = pyqtSignal(dict)
    cancelled = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._method = "file"

        self.setStyleSheet(f"background: {_BG};")

        # Outer stack: method-select (0) | input (1)
        self._outer = QStackedWidget()
        self._outer.setStyleSheet(f"background: {_BG};")

        # ── Page 0: Method selection ──────────────────────────────────────
        select_page = QWidget()
        select_page.setStyleSheet(f"background: {_BG};")
        select_layout = QVBoxLayout(select_page)
        select_layout.setContentsMargins(0, 0, 0, 0)
        select_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        center = QWidget()
        center.setStyleSheet("background: transparent;")
        center.setFixedWidth(560)
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        # Logo
        logo_lbl = QLabel(
            "<span style='font-size:18px; font-weight:800; color:#e8eaf0;'>"
            "LIBRE<span style='color:#001999'>IPTV</span></span>"
        )
        logo_lbl.setTextFormat(Qt.TextFormat.RichText)
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_lbl.setStyleSheet("background: transparent; border: none;")
        center_layout.addWidget(logo_lbl)

        subtitle = QLabel("Añadí tu primera fuente IPTV para comenzar")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(
            f"color: {_SEC}; font-size: 13px; background: transparent; border: none;"
        )
        center_layout.addSpacing(16)
        center_layout.addWidget(subtitle)
        center_layout.addSpacing(32)

        # Method cards — kept as QPushButtons styled as full-width cards
        self._tab_btns: dict[str, QPushButton] = {}
        card_container = QWidget()
        card_container.setStyleSheet("background: transparent;")
        cards_layout = QVBoxLayout(card_container)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(8)

        for key in _METHODS:
            meta = _METHOD_META[key]
            btn = QPushButton()
            btn.setCheckable(True)
            btn.setMinimumHeight(80)

            tag_text = "  ".join(f"[{t}]" for t in meta["tags"])
            btn.setText(
                f"{meta['icon']}  {meta['title']}\n"
                f"{meta['desc']}\n"
                f"{tag_text}"
            )
            btn.setStyleSheet(
                f"QPushButton {{"
                f"  background: {_ELEVATED}; color: {_TEXT};"
                f"  border: 1px solid {_BORDER}; border-left: 3px solid transparent;"
                f"  text-align: left; padding: 16px 20px; font-size: 13px;"
                f"  font-weight: 600;"
                f"}}"
                f"QPushButton:checked {{"
                f"  border-left: 3px solid {_ACCENT};"
                f"  background: rgba(0,25,153,0.08);"
                f"}}"
                f"QPushButton:hover:!checked {{"
                f"  background: rgba(255,255,255,0.03);"
                f"  border-color: {_ACCENT};"
                f"}}"
            )
            btn.clicked.connect(lambda _checked, k=key: self._select_and_go(k))
            self._tab_btns[key] = btn
            cards_layout.addWidget(btn)

        self._tab_btns["file"].setChecked(True)
        center_layout.addWidget(card_container)

        skip_lbl = QLabel("OMITIR →")
        skip_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        skip_lbl.setStyleSheet(
            f"color: {_DIM}; font-size: 10px; letter-spacing: 0.08em;"
            "background: transparent; border: none; padding-top: 16px;"
        )
        skip_lbl.mousePressEvent = lambda _: self.cancelled.emit()  # type: ignore[method-assign]
        center_layout.addSpacing(8)
        center_layout.addWidget(skip_lbl)

        select_layout.addStretch()
        select_layout.addWidget(center, alignment=Qt.AlignmentFlag.AlignCenter)
        select_layout.addStretch()
        self._outer.addWidget(select_page)

        # ── Page 1: Input ─────────────────────────────────────────────────
        input_page = QWidget()
        input_page.setStyleSheet(f"background: {_BG};")
        input_layout = QVBoxLayout(input_page)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        input_center = QWidget()
        input_center.setStyleSheet("background: transparent;")
        input_center.setFixedWidth(540)
        ic_layout = QVBoxLayout(input_center)
        ic_layout.setContentsMargins(0, 0, 0, 0)
        ic_layout.setSpacing(0)

        # Back button row
        back_row = QHBoxLayout()
        back_btn = QPushButton("← Volver")
        back_btn.setFlat(True)
        back_btn.setStyleSheet(
            f"color: {_SEC}; background: transparent; border: none;"
            "font-size: 12px; text-align: left; padding: 0;"
        )
        back_btn.clicked.connect(lambda: self._outer.setCurrentIndex(0))
        back_row.addWidget(back_btn)
        back_row.addStretch()
        ic_layout.addLayout(back_row)
        ic_layout.addSpacing(24)

        # Method-specific inputs
        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"background: transparent;")

        # Page 0: File
        file_page = QWidget()
        file_page.setStyleSheet("background: transparent;")
        fp_layout = QVBoxLayout(file_page)
        fp_layout.setContentsMargins(0, 0, 0, 0)
        fp_layout.setSpacing(12)

        fp_title = QLabel("IMPORTAR ARCHIVO M3U")
        fp_title.setStyleSheet(
            f"color: {_TEXT}; font-size: 16px; font-weight: 700;"
            "background: transparent; border: none;"
        )
        fp_layout.addWidget(fp_title)
        fp_layout.addSpacing(8)

        file_row = QHBoxLayout()
        file_row.setSpacing(8)
        self._file_input = QLineEdit()
        self._file_input.setPlaceholderText("Ruta al archivo .m3u / .m3u8")
        self._file_input.setFixedHeight(48)
        self._file_input.setStyleSheet(_INPUT_STYLE)
        browse_btn = QPushButton("Examinar…")
        browse_btn.setFixedHeight(48)
        browse_btn.setStyleSheet(
            f"background: {_ELEVATED}; color: {_TEXT}; border: 1px solid {_BORDER};"
            "padding: 0 16px; font-size: 12px; font-weight: 600;"
        )
        browse_btn.clicked.connect(self._browse_file)
        file_row.addWidget(self._file_input)
        file_row.addWidget(browse_btn)
        fp_layout.addLayout(file_row)

        hint = QLabel("Soporta .m3u y .m3u8 · Se procesa localmente")
        hint.setStyleSheet(
            f"color: {_DIM}; font-size: 10px; background: transparent; border: none;"
        )
        fp_layout.addWidget(hint)
        fp_layout.addStretch()
        self._stack.addWidget(file_page)

        # Page 1: URL
        url_page = QWidget()
        url_page.setStyleSheet("background: transparent;")
        up_layout = QVBoxLayout(url_page)
        up_layout.setContentsMargins(0, 0, 0, 0)
        up_layout.setSpacing(12)

        up_title = QLabel("IMPORTAR URL M3U")
        up_title.setStyleSheet(
            f"color: {_TEXT}; font-size: 16px; font-weight: 700;"
            "background: transparent; border: none;"
        )
        up_layout.addWidget(up_title)
        up_layout.addSpacing(8)

        url_label = QLabel("URL DE LA LISTA")
        url_label.setStyleSheet(
            f"color: {_DIM}; font-size: 9px; font-weight: 700; letter-spacing: 0.1em;"
            "background: transparent; border: none;"
        )
        up_layout.addWidget(url_label)
        self._url_input = QLineEdit()
        self._url_input.setPlaceholderText("https://proveedor.com/lista.m3u")
        self._url_input.setFixedHeight(48)
        self._url_input.setStyleSheet(_INPUT_STYLE)
        up_layout.addWidget(self._url_input)
        up_layout.addStretch()
        self._stack.addWidget(url_page)

        # Page 2: Xtream
        xtream_page = QWidget()
        xtream_page.setStyleSheet("background: transparent;")
        xp_layout = QVBoxLayout(xtream_page)
        xp_layout.setContentsMargins(0, 0, 0, 0)
        xp_layout.setSpacing(12)

        xp_title = QLabel("XTREAM CODES API")
        xp_title.setStyleSheet(
            f"color: {_TEXT}; font-size: 16px; font-weight: 700;"
            "background: transparent; border: none;"
        )
        xp_layout.addWidget(xp_title)
        xp_layout.addSpacing(8)

        for field_label, placeholder, attr in [
            ("SERVIDOR", "http://proveedor.com:8080", "_xtream_server"),
            ("USUARIO", "tu_usuario", "_xtream_user"),
            ("CONTRASEÑA", "••••••••", "_xtream_pass"),
        ]:
            lbl = QLabel(field_label)
            lbl.setStyleSheet(
                f"color: {_DIM}; font-size: 9px; font-weight: 700; letter-spacing: 0.1em;"
                "background: transparent; border: none;"
            )
            xp_layout.addWidget(lbl)
            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            inp.setFixedHeight(48)
            inp.setStyleSheet(_INPUT_STYLE)
            if attr == "_xtream_pass":
                inp.setEchoMode(QLineEdit.EchoMode.Password)
            setattr(self, attr, inp)
            xp_layout.addWidget(inp)

        xp_layout.addStretch()
        self._stack.addWidget(xtream_page)

        ic_layout.addWidget(self._stack)
        ic_layout.addSpacing(16)

        # Status
        self._status_label = QLabel("")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setStyleSheet(
            f"color: {_SEC}; font-size: 11px; background: transparent; border: none;"
        )
        ic_layout.addWidget(self._status_label)

        ic_layout.addSpacing(16)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setFixedHeight(48)
        cancel_btn.setStyleSheet(
            f"background: transparent; color: {_SEC};"
            f"border: 1px solid {_BORDER}; padding: 0 20px; font-size: 12px;"
        )
        cancel_btn.clicked.connect(self._cancel)
        import_btn = QPushButton("IMPORTAR")
        import_btn.setFixedHeight(48)
        import_btn.setStyleSheet(
            f"background: {_ACCENT}; color: #060810; border: none;"
            "padding: 0 24px; font-size: 12px; font-weight: 700; letter-spacing: 0.04em;"
        )
        import_btn.clicked.connect(self._trigger_import)
        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(import_btn)
        ic_layout.addLayout(btn_row)

        input_layout.addStretch()
        input_layout.addWidget(input_center, alignment=Qt.AlignmentFlag.AlignCenter)
        input_layout.addStretch()
        self._outer.addWidget(input_page)

        # Progress bar lives outside _outer so isVisible() works regardless of page
        self._progress_widget = QProgressBar()
        self._progress_widget.setRange(0, 0)
        self._progress_widget.setFixedHeight(2)
        self._progress_widget.setStyleSheet(
            f"QProgressBar {{ border: none; background: {_ELEVATED}; }}"
            f"QProgressBar::chunk {{ background: {_ACCENT}; }}"
        )
        self._progress_widget.setVisible(False)

        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.addWidget(self._outer)
        main.addWidget(self._progress_widget)

    # ── Public API ────────────────────────────────────────────────────────

    def selected_method(self) -> str:
        return self._method

    def select_method(self, method: str) -> None:
        if method not in _METHODS:
            return
        self._method = method
        for key, btn in self._tab_btns.items():
            btn.setChecked(key == method)
        self._stack.setCurrentIndex(_METHODS.index(method))

    def set_status(self, text: str) -> None:
        self._status_label.setText(text)

    def set_progress(self, visible: bool) -> None:
        self._progress_widget.setVisible(visible)

    # ── Internal ──────────────────────────────────────────────────────────

    def _select_and_go(self, method: str) -> None:
        self.select_method(method)
        self._outer.setCurrentIndex(1)

    def _browse_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar lista M3U",
            "",
            "Listas M3U (*.m3u *.m3u8);;Todos los archivos (*)",
        )
        if path:
            self._file_input.setText(path)

    def _trigger_import(self) -> None:
        if self._method == "file":
            path = self._file_input.text().strip()
            if not path:
                return
            self.import_requested.emit({"method": "file", "path": path})
        elif self._method == "url":
            url = self._url_input.text().strip()
            if not url:
                return
            self.import_requested.emit({"method": "url", "url": url})
        elif self._method == "xtream":
            self.import_requested.emit(
                {
                    "method": "xtream",
                    "server": self._xtream_server.text().strip(),
                    "username": self._xtream_user.text().strip(),
                    "password": self._xtream_pass.text().strip(),
                }
            )

    def _cancel(self) -> None:
        self.cancelled.emit()
