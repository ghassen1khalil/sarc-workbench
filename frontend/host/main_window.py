from __future__ import annotations

from pathlib import Path
from typing import Dict

import yaml
from PyQt6.QtWidgets import (
    QApplication,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QWidget,
)

from frontend.host.plugin_manager import PluginManager


class MainWindow(QMainWindow):
    def __init__(self, config_path: Path) -> None:
        super().__init__()
        self.setWindowTitle("Workbench Host")
        self.resize(900, 600)

        self.sidebar = QListWidget()
        self.sidebar.currentRowChanged.connect(self._on_plugin_selected)

        self.stack = QStackedWidget()

        self.setCentralWidget(self._build_layout())

        config = self._load_config(config_path)
        if not config:
            return

        plugin_manager = PluginManager(config.get("plugins", {}))
        self._plugins = plugin_manager.load_plugins()
        self._populate_plugins()

    def _build_layout(self) -> QWidget:
        container = QWidget()
        layout = container.layout()
        if layout is None:
            from PyQt6.QtWidgets import QHBoxLayout

            layout = QHBoxLayout(container)
        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack)
        layout.setStretch(1, 1)
        return container

    def _load_config(self, config_path: Path) -> Dict[str, object] | None:
        try:
            with config_path.open("r", encoding="utf-8") as config_file:
                return yaml.safe_load(config_file)
        except FileNotFoundError:
            QMessageBox.critical(
                self,
                "Configuration Missing",
                f"Configuration file not found: {config_path}",
            )
        except yaml.YAMLError as exc:
            QMessageBox.critical(
                self,
                "Configuration Error",
                f"Unable to parse configuration file.\n{exc}",
            )
        return None

    def _populate_plugins(self) -> None:
        self.sidebar.clear()
        self.stack.clear()
        if not self._plugins:
            QMessageBox.information(
                self,
                "No Plugins",
                "No plugins are enabled in the configuration.",
            )
            return
        for name, widget in self._plugins.items():
            self.stack.addWidget(widget)
            self.sidebar.addItem(QListWidgetItem(name))
        self.sidebar.setCurrentRow(0)

    def _on_plugin_selected(self, index: int) -> None:
        if index < 0:
            return
        self.stack.setCurrentIndex(index)


def run_app(config_path: Path) -> None:
    app = QApplication([])
    window = MainWindow(config_path)
    window.show()
    app.exec()
