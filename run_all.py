from __future__ import annotations

import subprocess
import sys
import time


def main() -> int:
    processes: list[subprocess.Popen[str]] = []
    try:
        core_service = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "backend.core_service.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
            ],
        )
        processes.append(core_service)

        req_checker = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "backend.plugins.requirements_checker.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8001",
            ],
        )
        processes.append(req_checker)

        time.sleep(0.5)

        frontend = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "frontend.host.main",
            ],
        )
        processes.append(frontend)

        for process in processes:
            process.wait()

        return 0
    except KeyboardInterrupt:
        return 0
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()


if __name__ == "__main__":
    raise SystemExit(main())
