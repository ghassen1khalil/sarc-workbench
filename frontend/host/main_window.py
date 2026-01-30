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
    QDockWidget,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtWidgets import QStyle

from .admin_panel import AdminWidget
from .log_viewer import LogConsole
from .plugin_manager import PluginManager


class MainWindow(QMainWindow):
    def __init__(self, config_path: Path) -> None:
        super().__init__()
        self.setWindowTitle("SARC Workbench")
        self.resize(900, 600)

        config = self._load_config(config_path)
        self._plugin_manager = PluginManager(config)
        active_plugins = self._plugin_manager.get_active_plugins()

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
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.log_console = LogConsole()
        self._add_log_dock()

        self._plugin_items: dict[str, QListWidgetItem] = {}
        self._plugin_widgets: dict[str, QWidget] = {}

        self._add_admin_panel(config)
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
            plugin_key = self._plugin_key_from_display(name)
            self._plugin_items[plugin_key] = item
            self._plugin_widgets[plugin_key] = widget

    def _switch_plugin(self, index: int) -> None:
        if index >= 0:
            self.stack.setCurrentIndex(index)

    def _add_admin_panel(self, config: dict) -> None:
        plugins_config = config.get("plugins", {})
        admin_widget = AdminWidget(
            api_base_url="http://127.0.0.1:8000",
            plugins_config=plugins_config,
        )
        admin_widget.plugin_toggled_signal.connect(self.on_plugin_toggled)

        item = QListWidgetItem("Administration")
        item.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.sidebar.addItem(item)
        self.stack.addWidget(admin_widget)

    def _add_log_dock(self) -> None:
        dock = QDockWidget("Logs", self)
        dock.setWidget(self.log_console)
        dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)

    def on_plugin_toggled(self, name: str, enabled: bool) -> None:
        if enabled:
            widget = self._plugin_manager.load_plugin_widget(name)
            if widget is None:
                self.status_bar.showMessage(
                    f"Impossible de charger le module {name}.", 4000
                )
                return

            if name in self._plugin_widgets:
                self.status_bar.showMessage(f"Module {name} déjà actif.", 3000)
                return

            display_name = self._display_name_from_key(name)
            item = QListWidgetItem(display_name)
            item.setIcon(self._plugin_icon(display_name))
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.sidebar.addItem(item)
            self.stack.addWidget(widget)
            self._plugin_items[name] = item
            self._plugin_widgets[name] = widget
            self.status_bar.showMessage(f"Module {display_name} activé.", 3000)
            return

        item = self._plugin_items.pop(name, None)
        widget = self._plugin_widgets.pop(name, None)
        if item is None or widget is None:
            self.status_bar.showMessage(f"Module {name} déjà désactivé.", 3000)
            return

        self._plugin_manager.unload_plugin_widget(name)
        widget_index = self.stack.indexOf(widget)
        if widget_index != -1:
            self.stack.removeWidget(widget)
        widget.deleteLater()

        row = self.sidebar.row(item)
        self.sidebar.takeItem(row)
        self.status_bar.showMessage(f"Module {name} désactivé.", 3000)

    def _plugin_icon(self, display_name: str):
        if display_name == "Requirements Checker":
            return self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        return self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogListView)

    @staticmethod
    def _display_name_from_key(plugin_key: str) -> str:
        if plugin_key == "requirements_checker":
            return "Requirements Checker"
        return plugin_key.replace("_", " ").title()

    @staticmethod
    def _plugin_key_from_display(display_name: str) -> str:
        if display_name == "Requirements Checker":
            return "requirements_checker"
        return display_name.lower().replace(" ", "_")

    def apply_theme(self, theme_name: str) -> None:
        _ = theme_name
        return

    def append_log(self, level: str, message: str) -> None:
        self.log_console.append_log(level, message)

    @staticmethod
    def _load_config(config_path: Path) -> dict:
        with config_path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        return data


def build_main_window() -> MainWindow:
    config_path = Path(__file__).resolve().parents[2] / "conf" / "application_config.yaml"
    return MainWindow(config_path)
