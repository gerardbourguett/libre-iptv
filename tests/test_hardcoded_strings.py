"""REQ-06: Validate zero hardcoded user-facing strings in src/ui/*.py."""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

# Known non-user-facing string literals that are exempt from translation
_EXACT_EXEMPTS = {
    "",
    " ",
    "  ",
    # Object names / style IDs
    "current_pin",
    "new_pin",
    "confirm_pin",
    "primary",
    "new_profile",
    "scroll_contents",
    "layout_toolbar",
    "ok_btn",
    # Single chars / symbols
    "1",
    "2",
    "4",
    "Q",
    "C",
    "?",
    # Layout symbols (design decision: not translated)
    "⬜  1",
    "⬛  2",
    "▦  4",
    # UI markers (language-independent symbols)
    "▼",
    "▶",
    "•",
    "●",
    "›",
    "▪",
    "◾",
    "■",
    "⬜",
    "▦",
    "★",
    "✕",
    "⭐",
    "🕐",
    "🔒",
    "⌫",
    "▶",
    "—",
    "–",
    # Common CSS color values
    "#0d0d0d",
    "#1a1a1a",
    "#1e1e1e",
    "#161616",
    "#2a2a2a",
    "#262626",
    "#3a3a3a",
    "#e0e0e0",
    "#9e9e9e",
    "#888888",
    "#888",
    "#555",
    "#757575",
    "#f44336",
    "#00bcd4",
    "#00e5ff",
    "#4caf50",
    "#000000",
    "#000",
    "#ffffff",
    # Font names
    "Segoe UI",
    # Settings keys
    "iptv-player",
    "window/geometry",
    "window/splitter_sizes",
    "playlist/last_path",
    "language/code",
    # File extensions
    ".png",
    ".png.tmp",
    # Brand names (should not be translated)
    "GitHub Sponsors",
    "Ko-fi",
    # Version fallback
    "0.2.0",
    # HTML fragments
    "<a href='",
    "</a>",
    # Format placeholders
    "{count}",
    "{name}",
    "{message}",
    "{version}",
    "{url}",
    # Internal constants that get translated at display time
    "Uncategorized",
    "__favorites__",
    "__recent__",
    # Log format strings (not user-facing)
    "EPG error: %s",
    # Symbolic PIN display (language-independent)
    "• • • •",
}

# Regex patterns for strings that are clearly not user-facing UI text
_NON_UI_PATTERNS = [
    re.compile(r"^#[0-9a-fA-F]{3,8}$"),  # hex color
    re.compile(r"^https?://"),  # URL
    re.compile(r"^\d+$"),  # pure digits
    re.compile(r"^[^\w\sáéíóúñÁÉÍÓÚÑ]+$"),  # only symbols (no letters)
    re.compile(r"^Q[A-Z][a-zA-Z0-9]*"),  # Qt class names
    re.compile(r"^[a-z_][a-z0-9_]*$"),  # python identifiers / object names
    re.compile(r"^rgba?\("),  # css color function
    re.compile(r"^\{[^{}]*\}$"),  # single braces placeholder like {count}
    re.compile(r"^\d+\.\d+\.\d+$"),  # semantic version numbers
]

# Heuristic: strings that contain these substrings are likely style sheets or code
_CODE_SUBSTRINGS = [
    "background:",
    "color:",
    "border:",
    "padding:",
    "margin:",
    "font-size:",
    "font-weight:",
    "border-radius:",
    "outline:",
    "spacing:",
    "min-width:",
    "min-height:",
    "max-width:",
    "max-height:",
    "border-top:",
    "border-bottom:",
    "border-left:",
    "border-right:",
    "border-color:",
    "border-style:",
    "text-decoration:",
    "letter-spacing:",
    "line-height:",
    "QWidget",
    "QDialog",
    "QLabel",
    "QLineEdit",
    "QPushButton",
    "QListWidget",
    "QToolButton",
    "QMenu",
    "QToolBar",
    "QStatusBar",
    "QSplitter",
    "QScrollArea",
    "::item",
    "::handle",
    "::item:selected",
    "::item:hover",
    "QToolButton:checked",
    "QPushButton:hover",
    "QPushButton:pressed",
    "QLineEdit:focus",
    "QMenu::item:selected",
    "importlib.metadata",
    "PackageNotFoundError",
]


class _HardcodedStringFinder(ast.NodeVisitor):
    def __init__(self) -> None:
        self.findings: list[str] = []
        self._call_stack: list[ast.Call] = []
        self._parent_stack: list[ast.AST] = []

    def visit(self, node: ast.AST) -> None:
        self._parent_stack.append(node)
        super().visit(node)
        self._parent_stack.pop()

    def visit_Call(self, node: ast.Call) -> None:
        self._call_stack.append(node)
        self.generic_visit(node)
        self._call_stack.pop()

    def visit_Constant(self, node: ast.Constant) -> None:
        if not isinstance(node.value, str):
            return
        s = node.value.strip()
        if self._is_docstring(node):
            return
        if self._is_inside_t_call():
            return
        if self._is_exempt(s):
            return
        self.findings.append(s)

    def _is_docstring(self, node: ast.Constant) -> bool:
        """Detect if this string constant is a docstring."""
        if len(self._parent_stack) < 3:
            return False
        # parent_stack[-1] is the Constant itself
        # parent_stack[-2] should be Expr
        # parent_stack[-3] should be Module/ClassDef/FunctionDef
        expr_node = self._parent_stack[-2]
        container = self._parent_stack[-3]
        if not isinstance(expr_node, ast.Expr):
            return False
        if isinstance(
            container,
            (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef),
        ):
            # Check if this Expr is the first statement in the body
            if container.body and container.body[0] is expr_node:
                return True
        return False

    def _is_inside_t_call(self) -> bool:
        for call in self._call_stack:
            func = call.func
            if isinstance(func, ast.Name) and func.id == "t":
                return True
            if isinstance(func, ast.Attribute) and func.attr == "t":
                return True
        return False

    def _is_exempt(self, s: str) -> bool:
        if s in _EXACT_EXEMPTS:
            return True
        if len(s) < 2:
            return True
        for pat in _NON_UI_PATTERNS:
            if pat.match(s):
                return True
        for substr in _CODE_SUBSTRINGS:
            if substr in s:
                return True
        return False


def _scan_file(path: Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    finder = _HardcodedStringFinder()
    finder.visit(tree)
    return finder.findings


class TestZeroHardcodedStrings:
    """REQ-06: Zero hardcoded user-facing strings in src/ui/*.py outside t() calls."""

    def test_no_hardcoded_ui_strings_in_src_ui(self):
        ui_dir = Path(__file__).parent.parent / "src" / "ui"
        assert ui_dir.exists(), f"UI directory not found: {ui_dir}"

        all_findings: dict[str, list[str]] = {}
        for py_file in sorted(ui_dir.glob("*.py")):
            findings = _scan_file(py_file)
            if findings:
                all_findings[str(py_file.relative_to(ui_dir.parent.parent))] = findings

        if all_findings:
            msg_lines = ["Found hardcoded user-facing strings outside t() calls:"]
            for file_path, strings in all_findings.items():
                for s in strings:
                    msg_lines.append(f"  {file_path}: '{s}'")
            pytest.fail("\n".join(msg_lines))
