from __future__ import annotations

from typing import Dict, List, Tuple, Type

from PyQt6.QtWidgets import QWidget

from frontend.plugins.requirements_checker.ui import RequirementsCheckerWidget


class PluginManager:
    def __init__(self, config: dict) -> None:
        self.config = config
        self._instances: Dict[str, QWidget] = {}

    def get_active_plugins(self) -> List[Tuple[str, QWidget]]:
        plugins_config = self.config.get("plugins", {})
        plugins: List[Tuple[str, QWidget]] = []

        plugin_registry: Dict[str, Tuple[str, Type[QWidget]]] = {
            "requirements_checker": ("Requirements Checker", RequirementsCheckerWidget),
        }

        for plugin_key, (display_name, widget_cls) in plugin_registry.items():
            plugin_settings = plugins_config.get(plugin_key, {})
            if not plugin_settings.get("enabled", False):
                continue

            widget = self.load_plugin_widget(plugin_key)
            if widget is None:
                continue
            plugins.append((display_name, widget))

        return plugins

    def load_plugin_widget(self, plugin_name: str) -> QWidget | None:
        existing = self._instances.get(plugin_name)
        if existing is not None:
            return existing

        plugins_config = self.config.get("plugins", {})
        plugin_settings = plugins_config.get(plugin_name, {})

        plugin_registry: Dict[str, Type[QWidget]] = {
            "requirements_checker": RequirementsCheckerWidget,
        }

        widget_cls = plugin_registry.get(plugin_name)
        if widget_cls is None:
            return None

        api_url = self._build_api_url(plugin_settings)
        try:
            widget = widget_cls(api_url)
        except Exception:
            return None

        self._instances[plugin_name] = widget
        return widget

    def get_plugin_widget(self, plugin_name: str) -> QWidget | None:
        return self._instances.get(plugin_name)

    @staticmethod
    def _build_api_url(plugin_settings: dict) -> str:
        host = plugin_settings.get("host", "127.0.0.1")
        port = plugin_settings.get("port", 8001)
        return f"http://{host}:{port}/system/stats"
