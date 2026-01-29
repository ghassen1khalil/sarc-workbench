from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import yaml
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

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
        self.sidebar.setFixedWidth(220)
        self.sidebar.currentRowChanged.connect(self._switch_plugin)

        self.stack = QStackedWidget()
        self._populate_plugins(active_plugins)

        layout = QHBoxLayout()
        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack, stretch=1)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        if active_plugins:
            self.sidebar.setCurrentRow(0)

    def _populate_plugins(self, plugins: List[Tuple[str, QWidget]]) -> None:
        for name, widget in plugins:
            item = QListWidgetItem(name)
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
