from __future__ import annotations

from typing import Any, Dict

import requests
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class RequirementsCheckerWidget(QWidget):
    def __init__(self, api_url: str = "http://localhost:8001/system/stats") -> None:
        super().__init__()
        self.api_url = api_url

        self.status_label = QLabel("Ready")
        self.cpu_value = QLabel("-")
        self.memory_total_value = QLabel("-")
        self.memory_used_value = QLabel("-")
        self.memory_percent_value = QLabel("-")
        self.disk_total_value = QLabel("-")
        self.disk_used_value = QLabel("-")
        self.disk_percent_value = QLabel("-")

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_stats)

        grid = QGridLayout()
        grid.addWidget(QLabel("CPU Usage (%):"), 0, 0)
        grid.addWidget(self.cpu_value, 0, 1)
        grid.addWidget(QLabel("Memory Total (bytes):"), 1, 0)
        grid.addWidget(self.memory_total_value, 1, 1)
        grid.addWidget(QLabel("Memory Used (bytes):"), 2, 0)
        grid.addWidget(self.memory_used_value, 2, 1)
        grid.addWidget(QLabel("Memory Usage (%):"), 3, 0)
        grid.addWidget(self.memory_percent_value, 3, 1)
        grid.addWidget(QLabel("Disk Total (bytes):"), 4, 0)
        grid.addWidget(self.disk_total_value, 4, 1)
        grid.addWidget(QLabel("Disk Used (bytes):"), 5, 0)
        grid.addWidget(self.disk_used_value, 5, 1)
        grid.addWidget(QLabel("Disk Usage (%):"), 6, 0)
        grid.addWidget(self.disk_percent_value, 6, 1)

        layout = QVBoxLayout()
        layout.addLayout(grid)
        layout.addWidget(self.refresh_button, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

    def refresh_stats(self) -> None:
        try:
            response = requests.get(self.api_url, timeout=3)
            response.raise_for_status()
        except requests.RequestException as exc:
            self.status_label.setText(f"Error: {exc}")
            return

        data: Dict[str, Any] = response.json()
        self._update_values(data)
        self.status_label.setText("Updated")

    def _update_values(self, data: Dict[str, Any]) -> None:
        cpu = data.get("cpu", {})
        memory = data.get("memory", {})
        disk = data.get("disk", {})

        self.cpu_value.setText(str(cpu.get("percent", "-")))
        self.memory_total_value.setText(str(memory.get("total", "-")))
        self.memory_used_value.setText(str(memory.get("used", "-")))
        self.memory_percent_value.setText(str(memory.get("percent", "-")))
        self.disk_total_value.setText(str(disk.get("total", "-")))
        self.disk_used_value.setText(str(disk.get("used", "-")))
        self.disk_percent_value.setText(str(disk.get("percent", "-")))
