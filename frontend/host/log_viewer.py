from __future__ import annotations

from PyQt6.QtGui import QColor, QTextCharFormat, QTextCursor
from PyQt6.QtWidgets import QPlainTextEdit


class LogConsole(QPlainTextEdit):
    def __init__(self) -> None:
        super().__init__()
        self.setReadOnly(True)
        self.setStyleSheet(
            "background-color: #0b0b0b; color: #f0f0f0; font-family: 'Courier';"
        )

    def append_log(self, level: str, message: str) -> None:
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.setCharFormat(self._format_for_level(level))
        cursor.insertText(f"[{level}] {message}\n")
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    @staticmethod
    def _format_for_level(level: str) -> QTextCharFormat:
        fmt = QTextCharFormat()
        level_name = level.upper()
        if level_name in {"ERROR", "CRITICAL"}:
            fmt.setForeground(QColor("#ff5c5c"))
        elif level_name == "WARNING":
            fmt.setForeground(QColor("#ffcc66"))
        elif level_name == "INFO":
            fmt.setForeground(QColor("#7cd3ff"))
        else:
            fmt.setForeground(QColor("#d9d9d9"))
        return fmt
