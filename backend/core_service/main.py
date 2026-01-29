from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .config_manager import load_config

app = FastAPI(title="SARC Workbench Core Service")


@app.get("/config")
async def get_config() -> dict:
    try:
        return load_config()
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
