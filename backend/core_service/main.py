from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI

from config_manager import ConfigManager

app = FastAPI(title="Workbench Core Service", version="1.0.0")

CONFIG_PATH = Path(__file__).resolve().parents[2] / "conf" / "application_config.yaml"
config_manager = ConfigManager(CONFIG_PATH)


@app.get("/config", response_model=Dict[str, Any])
async def get_config() -> Dict[str, Any]:
    return config_manager.load()
