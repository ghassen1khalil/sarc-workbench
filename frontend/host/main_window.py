from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import yaml
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtWidgets import QStyle

from .plugin_manager import PluginManager


class MainWindow(QMainWindow):
    def __init__(self, config_path: Path) -> None:
        super().__init__()
        self.setWindowTitle("SARC Workbench")
        self.resize(900, 600)

        config = self._load_config(config_path)
        plugin_manager = PluginManager(config)
        active_plugins = plugin_manager.get_active_plugins()

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(240)
        self.sidebar.setSpacing(4)
        self.sidebar.setStyleSheet(
            "QListWidget { background: #f6f7fb; border: none; }"
            "QListWidget::item { padding: 8px; border-radius: 6px; }"
            "QListWidget::item:selected { background: #dfe7ff; color: #1f2d5a; }"
        )
        self.sidebar.currentRowChanged.connect(self._switch_plugin)

        self.stack = QStackedWidget()
        self._populate_plugins(active_plugins)

        sidebar_header = QLabel("Modules")
        sidebar_header.setStyleSheet("font-weight: 600; padding: 6px;")

        sidebar_container = QWidget()
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(6, 6, 6, 6)
        sidebar_layout.addWidget(sidebar_header)
        sidebar_layout.addWidget(self.sidebar)
        sidebar_container.setLayout(sidebar_layout)

        layout = QHBoxLayout()
        layout.addWidget(sidebar_container)
        layout.addWidget(self.stack, stretch=1)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        if active_plugins:
            self.sidebar.setCurrentRow(0)

    def _populate_plugins(self, plugins: List[Tuple[str, QWidget]]) -> None:
        style = QApplication.style()
        for name, widget in plugins:
            item = QListWidgetItem(name)
            if name == "Requirements Checker":
                item.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.sidebar.addItem(item)
            self.stack.addWidget(widget)

    def _switch_plugin(self, index: int) -> None:
        if index >= 0:
            self.stack.setCurrentIndex(index)

    @staticmethod
    def _load_config(config_path: Path) -> dict:
        with config_path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        return data


def build_main_window() -> MainWindow:
    config_path = Path(__file__).resolve().parents[2] / "conf" / "application_config.yaml"
    return MainWindow(config_path)
