from __future__ import annotations

from typing import Any, Dict

import psutil


def get_system_stats() -> Dict[str, Any]:
    cpu_percent = psutil.cpu_percent(interval=0.2)
    virtual_memory = psutil.virtual_memory()
    disk_usage = psutil.disk_usage("/")

    return {
        "cpu": {
            "percent": cpu_percent,
        },
        "memory": {
            "total": virtual_memory.total,
            "used": virtual_memory.used,
            "percent": virtual_memory.percent,
        },
        "disk": {
            "total": disk_usage.total,
            "used": disk_usage.used,
            "percent": disk_usage.percent,
        },
    }
