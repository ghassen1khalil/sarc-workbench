from __future__ import annotations

from typing import Any, Dict

import requests
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QStyle,
    QVBoxLayout,
    QWidget,
)


class RequirementsCheckerWidget(QWidget):
    def __init__(self, api_url: str = "http://localhost:8001/system/stats") -> None:
        super().__init__()
        self.api_url = api_url

        self.header_label = QLabel("Requirements Checker")
        self.header_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        self.subtitle_label = QLabel("Vérifiez rapidement les ressources système disponibles.")
        self.subtitle_label.setStyleSheet("color: #5a5a5a;")

        self.status_label = QLabel("Prêt")
        self.status_label.setStyleSheet("color: #2f6f2f;")
        self.status_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.cpu_percent_bar = QProgressBar()
        self.cpu_percent_bar.setRange(0, 100)
        self.cpu_percent_bar.setFormat("%p%")
        self.cpu_percent_bar.setValue(0)

        self.memory_total_value = QLabel("-")
        self.memory_used_value = QLabel("-")
        self.memory_percent_bar = QProgressBar()
        self.memory_percent_bar.setRange(0, 100)
        self.memory_percent_bar.setFormat("%p%")
        self.memory_percent_bar.setValue(0)

        self.disk_total_value = QLabel("-")
        self.disk_used_value = QLabel("-")
        self.disk_percent_bar = QProgressBar()
        self.disk_percent_bar.setRange(0, 100)
        self.disk_percent_bar.setFormat("%p%")
        self.disk_percent_bar.setValue(0)

        self.refresh_button = QPushButton("Actualiser")
        self.refresh_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        self.refresh_button.clicked.connect(self.refresh_stats)

        cpu_group = QGroupBox("CPU")
        cpu_layout = QVBoxLayout()
        cpu_layout.addWidget(QLabel("Utilisation"))
        cpu_layout.addWidget(self.cpu_percent_bar)
        cpu_group.setLayout(cpu_layout)

        memory_group = QGroupBox("Mémoire")
        memory_grid = QGridLayout()
        memory_grid.addWidget(QLabel("Total"), 0, 0)
        memory_grid.addWidget(self.memory_total_value, 0, 1)
        memory_grid.addWidget(QLabel("Utilisée"), 1, 0)
        memory_grid.addWidget(self.memory_used_value, 1, 1)
        memory_grid.addWidget(QLabel("Utilisation"), 2, 0)
        memory_grid.addWidget(self.memory_percent_bar, 2, 1)
        memory_group.setLayout(memory_grid)

        disk_group = QGroupBox("Disque")
        disk_grid = QGridLayout()
        disk_grid.addWidget(QLabel("Total"), 0, 0)
        disk_grid.addWidget(self.disk_total_value, 0, 1)
        disk_grid.addWidget(QLabel("Utilisé"), 1, 0)
        disk_grid.addWidget(self.disk_used_value, 1, 1)
        disk_grid.addWidget(QLabel("Utilisation"), 2, 0)
        disk_grid.addWidget(self.disk_percent_bar, 2, 1)
        disk_group.setLayout(disk_grid)

        groups_layout = QHBoxLayout()
        groups_layout.addWidget(cpu_group)
        groups_layout.addWidget(memory_group)
        groups_layout.addWidget(disk_group)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)

        layout = QVBoxLayout()
        layout.addWidget(self.header_label)
        layout.addWidget(self.subtitle_label)
        layout.addWidget(divider)
        layout.addLayout(groups_layout)
        layout.addWidget(self.refresh_button, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.status_label)
        layout.addStretch()
        self.setLayout(layout)

    def refresh_stats(self) -> None:
        self.status_label.setText("Mise à jour en cours...")
        self.status_label.setStyleSheet("color: #4a4a4a;")
        try:
            response = requests.get(self.api_url, timeout=3)
            response.raise_for_status()
        except requests.RequestException as exc:
            self.status_label.setText(f"Erreur: {exc}")
            self.status_label.setStyleSheet("color: #a11a1a;")
            return

        data: Dict[str, Any] = response.json()
        self._update_values(data)
        self.status_label.setText("Données mises à jour.")
        self.status_label.setStyleSheet("color: #2f6f2f;")

    def _update_values(self, data: Dict[str, Any]) -> None:
        cpu = data.get("cpu", {})
        memory = data.get("memory", {})
        disk = data.get("disk", {})

        self.cpu_percent_bar.setValue(int(cpu.get("percent", 0) or 0))
        self.memory_total_value.setText(self._format_bytes(memory.get("total")))
        self.memory_used_value.setText(self._format_bytes(memory.get("used")))
        self.memory_percent_bar.setValue(int(memory.get("percent", 0) or 0))
        self.disk_total_value.setText(self._format_bytes(disk.get("total")))
        self.disk_used_value.setText(self._format_bytes(disk.get("used")))
        self.disk_percent_bar.setValue(int(disk.get("percent", 0) or 0))

    @staticmethod
    def _format_bytes(value: Any) -> str:
        if not isinstance(value, (int, float)):
            return "-"

        size = float(value)
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
