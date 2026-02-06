from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
import yaml
from fastapi import FastAPI, HTTPException

from .service import get_system_stats

MODULE_NAME = "requirements_checker"


def _load_core_service_url() -> str:
    config_path = Path(__file__).resolve().parents[2] / "conf" / "application_config.yaml"
    try:
        with config_path.open("r", encoding="utf-8") as handle:
            raw_config: dict[str, Any] = yaml.safe_load(handle) or {}
    except FileNotFoundError:
        return "http://127.0.0.1:8000"

    core_config = raw_config.get("core_service", {})
    host = core_config.get("host", "127.0.0.1")
    port = core_config.get("port", 8000)
    return f"http://{host}:{port}"


CORE_SERVICE_URL = _load_core_service_url()
logger = logging.getLogger(MODULE_NAME)


def _build_log_message(message: str) -> str:
    timestamp = datetime.now(timezone.utc).isoformat()
    return f"{timestamp} - {MODULE_NAME} - {message}"


def _post_log(level: str, message: str) -> None:
    payload = {
        "name": MODULE_NAME,
        "level": level.upper(),
        "message": _build_log_message(message),
    }
    try:
        requests.post(
            f"{CORE_SERVICE_URL}/logs",
            json=payload,
            timeout=2,
        ).raise_for_status()
    except requests.RequestException:
        logger.debug("Impossible d'envoyer le log au Core Service", exc_info=True)


app = FastAPI(title="Requirements Checker Service")


@app.get("/system/stats")
def system_stats() -> dict:
    _post_log("INFO", "Lancement de la vérification des prérequis système.")
    try:
        return get_system_stats()
    except PermissionError as exc:
        _post_log("ERROR", f"Accès refusé lors de la vérification: {exc}")
        raise HTTPException(status_code=403, detail="Accès refusé lors de la vérification.") from exc
    except Exception as exc:
        _post_log("ERROR", f"Erreur inattendue lors de la vérification: {exc}")
        raise HTTPException(status_code=500, detail="Erreur interne pendant la vérification.") from exc
