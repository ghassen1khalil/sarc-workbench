from __future__ import annotations

from typing import Dict

from PyQt6.QtWidgets import QWidget

from frontend.plugins.requirements_checker.ui import RequirementsCheckerWidget


class PluginManager:
    def __init__(self, plugin_config: Dict[str, Dict[str, object]]) -> None:
        self.plugin_config = plugin_config

    def load_plugins(self) -> Dict[str, QWidget]:
        widgets: Dict[str, QWidget] = {}

        requirements_config = self.plugin_config.get("requirements_checker")
        if requirements_config and requirements_config.get("enabled"):
            host = requirements_config.get("host", "127.0.0.1")
            port = requirements_config.get("port", 8001)
            api_base_url = f"http://{host}:{port}"
            widgets["Requirements Checker"] = RequirementsCheckerWidget(api_base_url)

        return widgets
