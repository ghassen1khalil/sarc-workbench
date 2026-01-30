from __future__ import annotations

from pathlib import Path

import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .config_manager import load_config

LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "workbench.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8")],
)

logger = logging.getLogger("core_service")

app = FastAPI(title="SARC Workbench Core Service")


class LogEntry(BaseModel):
    name: str
    level: str
    message: str


@app.get("/config")
async def get_config() -> dict:
    try:
        return load_config()
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/logs")
async def create_log(entry: LogEntry) -> dict:
    level_name = entry.level.upper()
    level = logging.getLevelName(level_name)
    if isinstance(level, str):
        level = logging.INFO
    logging.getLogger(entry.name).log(level, entry.message)
    return {"status": "ok"}
