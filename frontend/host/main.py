from __future__ import annotations

import sys
import threading
import traceback

import requests

from PyQt6.QtWidgets import QApplication

from .main_window import build_main_window


def main() -> int:
    app = QApplication(sys.argv)
    window = build_main_window()

    def excepthook(exc_type, exc_value, exc_traceback) -> None:
        formatted = "".join(
            traceback.format_exception(exc_type, exc_value, exc_traceback)
        ).strip()
        window.append_log("ERROR", formatted)

        def send_log() -> None:
            try:
                requests.post(
                    "http://127.0.0.1:8000/logs",
                    json={
                        "name": "frontend",
                        "level": "ERROR",
                        "message": formatted,
                    },
                    timeout=2,
                )
            except requests.RequestException:
                return

        threading.Thread(target=send_log, daemon=True).start()

    sys.excepthook = excepthook

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
