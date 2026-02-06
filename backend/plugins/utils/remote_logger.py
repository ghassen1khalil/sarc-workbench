from __future__ import annotations

import logging
import threading
from typing import Optional

import requests


class RemoteLogHandler(logging.Handler):
    def __init__(self, core_service_url: str, timeout: float = 2.0) -> None:
        super().__init__()
        self.core_service_url = core_service_url.rstrip("/")
        self.timeout = timeout

    def emit(self, record: logging.LogRecord) -> None:
        message = self.format(record)
        payload = {
            "name": record.name,
            "level": record.levelname,
            "message": message,
        }
        thread = threading.Thread(
            target=self._send,
            args=(payload,),
            daemon=True,
        )
        thread.start()

    def _send(self, payload: dict) -> None:
        try:
            requests.post(
                f"{self.core_service_url}/logs",
                json=payload,
                timeout=self.timeout,
            )
        except requests.RequestException:
            return


def configure_remote_logging(
    logger: logging.Logger,
    core_service_url: str,
    level: int = logging.INFO,
    formatter: Optional[logging.Formatter] = None,
) -> RemoteLogHandler:
    handler = RemoteLogHandler(core_service_url)
    handler.setLevel(level)
    if formatter is None:
        formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return handler
