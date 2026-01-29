from __future__ import annotations

from fastapi import FastAPI

from .service import get_system_stats

app = FastAPI(title="Requirements Checker Service")


@app.get("/system/stats")
async def system_stats() -> dict:
    return get_system_stats()
