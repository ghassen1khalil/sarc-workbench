from __future__ import annotations

import threading
from typing import Dict

import requests
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class AdminWidget(QWidget):
    plugin_toggled_signal = pyqtSignal(str, bool)

    def __init__(self, api_base_url: str, plugins_config: dict) -> None:
        super().__init__()
        self.api_base_url = api_base_url.rstrip("/")
        self._plugins_config = plugins_config
        self._checkboxes: Dict[str, QCheckBox] = {}

        tabs = QTabWidget()
        tabs.addTab(self._build_general_tab(), "Général")
        tabs.addTab(self._build_plugins_tab(), "Plugins")
        tabs.addTab(self._build_logs_tab(), "Logs")

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        self.setLayout(layout)

    def _build_general_tab(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Paramètres globaux (bientôt disponibles)."))
        layout.addStretch()
        container.setLayout(layout)
        return container

    def _build_plugins_tab(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout()

        group = QGroupBox("Modules disponibles")
        form = QFormLayout()

        for plugin_name, settings in self._plugins_config.items():
            checkbox = QCheckBox()
            checkbox.setChecked(bool(settings.get("enabled", False)))
            checkbox.stateChanged.connect(
                lambda state, name=plugin_name: self._on_plugin_state_changed(name, state)
            )
            form.addRow(plugin_name.replace("_", " ").title(), checkbox)
            self._checkboxes[plugin_name] = checkbox

        group.setLayout(form)
        layout.addWidget(group)
        layout.addStretch()
        container.setLayout(layout)
        return container

    def _build_logs_tab(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Historique des actions (placeholder)."))
        layout.addStretch()
        container.setLayout(layout)
        return container

    def _on_plugin_state_changed(self, plugin_name: str, state: int) -> None:
        is_checked = state == Qt.CheckState.Checked.value
        self.plugin_toggled_signal.emit(plugin_name, is_checked)

        threading.Thread(
            target=self._post_toggle_request,
            args=(plugin_name, is_checked),
            daemon=True,
        ).start()

    def _post_toggle_request(self, plugin_name: str, enabled: bool) -> None:
        url = f"{self.api_base_url}/admin/plugins/{plugin_name}/toggle"
        try:
            requests.post(url, json={"enabled": enabled}, timeout=2)
        except requests.RequestException:
            return
