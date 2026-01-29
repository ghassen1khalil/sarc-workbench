from __future__ import annotations

from typing import Any, Dict

import requests
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class RequirementsCheckerWidget(QWidget):
    def __init__(self, api_base_url: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.api_base_url = api_base_url.rstrip("/")
        self._labels: Dict[str, QLabel] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        stats_group = QGroupBox("System Resources")
        grid = QGridLayout(stats_group)

        self._add_stat_row(grid, "CPU Usage", "cpu_usage")
        self._add_stat_row(grid, "RAM Total", "ram_total")
        self._add_stat_row(grid, "RAM Used", "ram_used")
        self._add_stat_row(grid, "RAM Percent", "ram_percent")
        self._add_stat_row(grid, "Disk Total", "disk_total")
        self._add_stat_row(grid, "Disk Used", "disk_used")
        self._add_stat_row(grid, "Disk Percent", "disk_percent")

        layout.addWidget(stats_group)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_stats)
        layout.addWidget(self.refresh_button, alignment=Qt.AlignmentFlag.AlignRight)

    def _add_stat_row(self, layout: QGridLayout, label_text: str, key: str) -> None:
        row = layout.rowCount()
        label = QLabel(f"{label_text}:")
        value = QLabel("-")
        value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label, row, 0)
        layout.addWidget(value, row, 1)
        self._labels[key] = value

    def refresh_stats(self) -> None:
        try:
            response = requests.get(f"{self.api_base_url}/system/stats", timeout=5)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            QMessageBox.warning(
                self,
                "Connection Error",
                f"Unable to reach the Requirements Checker service.\n{exc}",
            )
            return
        except ValueError:
            QMessageBox.warning(
                self,
                "Invalid Response",
                "Received a non-JSON response from the service.",
            )
            return

        self._update_labels(data)

    def _update_labels(self, data: Dict[str, Any]) -> None:
        cpu = data.get("cpu", {})
        ram = data.get("ram", {})
        disk = data.get("disk", {})

        self._labels["cpu_usage"].setText(f"{cpu.get('percent', '-') }%")
        self._labels["ram_total"].setText(self._format_bytes(ram.get("total")))
        self._labels["ram_used"].setText(self._format_bytes(ram.get("used")))
        self._labels["ram_percent"].setText(f"{ram.get('percent', '-') }%")
        self._labels["disk_total"].setText(self._format_bytes(disk.get("total")))
        self._labels["disk_used"].setText(self._format_bytes(disk.get("used")))
        self._labels["disk_percent"].setText(f"{disk.get('percent', '-') }%")

    @staticmethod
    def _format_bytes(value: Any) -> str:
        if not isinstance(value, (int, float)):
            return "-"
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if value < 1024:
                return f"{value:.2f} {unit}"
            value /= 1024
        return f"{value:.2f} PB"
