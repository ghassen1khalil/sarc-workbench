from pathlib import Path
from typing import Any, Dict

import yaml


class ConfigManager:
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path

    def load(self) -> Dict[str, Any]:
        with self.config_path.open("r", encoding="utf-8") as config_file:
            return yaml.safe_load(config_file)
