from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml


CONFIG_PATH = Path(__file__).resolve().parents[2] / "conf" / "application_config.yaml"


def load_config(config_path: Path = CONFIG_PATH) -> Dict[str, Any]:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    if not isinstance(data, dict):
        raise ValueError("Configuration root must be a mapping")

    return data
