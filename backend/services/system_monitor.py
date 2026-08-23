import os
import shutil
import time
from datetime import datetime

try:
    import psutil
except ImportError:
    psutil = None


AUTOMATION_NAME = "SYSTEM_RESOURCE_MONITOR"


def _get_cpu():
    if psutil:
        return psutil.cpu_percent(interval=0.2)

    return None


def _get_memory():
    if psutil:
        memory = psutil.virtual_memory()
        return {
            "percent": memory.percent,
            "total_bytes": memory.total,
            "available_bytes": memory.available,
            "used_bytes": memory.used,
        }

    return None


def _get_disk():
    if psutil:
        disk = psutil.disk_usage("/")
        return {
            "percent": disk.percent,
            "total_bytes": disk.total,
            "used_bytes": disk.used,
            "free_bytes": disk.free,
        }

    usage = shutil.disk_usage("/")
    percent = (
        usage.used / usage.total * 100
        if usage.total
        else 0
    )

    return {
        "percent": round(percent, 2),
        "total_bytes": usage.total,
        "used_bytes": usage.used,
        "free_bytes": usage.free,
    }


def _get_uptime():
    if psutil:
        boot_time = psutil.boot_time()
        seconds = max(
            0,
            time.time() - boot_time
        )
    else:
        with open("/proc/uptime", "r") as file:
            seconds = float(
                file.readline().split()[0]
            )

    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)

    return {
        "seconds": int(seconds),
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "formatted": (
            f"{days}d {hours}h {minutes}m"
        ),
    }


def _get_service_status():
    import subprocess

    services = {}

    candidates = [
        "ssh",
        "sshd",
        "cron",
    ]

    for service_name in candidates:

        try:
            result = subprocess.run(
                [
                    "systemctl",
                    "is-active",
                    service_name,
                ],
                capture_output=True,
                text=True,
                timeout=3,
            )

            status = result.stdout.strip()

            if not status:
                status = "NOT_FOUND"

            services[service_name] = {
                "status": status,
                "running": status == "active",
            }

        except (
            subprocess.TimeoutExpired,
            OSError,
        ):

            services[service_name] = {
                "status": "UNKNOWN",
                "running": None,
            }

    return services

def run_system_monitor():
    """
    Collect host-level system monitoring metrics.

    Monitors:
    - CPU utilization
    - Memory utilization
    - Disk utilization
    - System uptime
    - Monitored service status
    """

    cpu_percent = _get_cpu()
    memory = _get_memory()
    disk = _get_disk()
    uptime = _get_uptime()
    services = _get_service_status()

    findings = []
    status = "HEALTHY"

    if cpu_percent is not None:
        if cpu_percent >= 90:
            status = "CRITICAL"
            findings.append(
                f"CPU utilization is critically high "
                f"at {cpu_percent:.1f}%."
            )
        elif cpu_percent >= 80:
            status = "WARNING"
            findings.append(
                f"CPU utilization is high "
                f"at {cpu_percent:.1f}%."
            )

    if memory:
        memory_percent = memory["percent"]

        if memory_percent >= 90:
            status = "CRITICAL"
            findings.append(
                f"Memory utilization is critically high "
                f"at {memory_percent:.1f}%."
            )
        elif memory_percent >= 80:
            if status != "CRITICAL":
                status = "WARNING"

            findings.append(
                f"Memory utilization is high "
                f"at {memory_percent:.1f}%."
            )

    if disk:
        disk_percent = disk["percent"]

        if disk_percent >= 90:
            status = "CRITICAL"
            findings.append(
                f"Disk utilization is critically high "
                f"at {disk_percent:.1f}%."
            )
        elif disk_percent >= 80:
            if status != "CRITICAL":
                status = "WARNING"

            findings.append(
                f"Disk utilization is high "
                f"at {disk_percent:.1f}%."
            )

    if not findings:
        findings.append(
            "System resource utilization is "
            "within configured thresholds."
        )

    return {
        "automation_name": AUTOMATION_NAME,
        "execution_time": datetime.utcnow().isoformat(),
        "status": status,
        "summary": (
            f"System monitor status: {status}. "
            f"CPU: {cpu_percent if cpu_percent is not None else 'N/A'}%. "
            f"Memory: "
            f"{memory['percent'] if memory else 'N/A'}%. "
            f"Disk: "
            f"{disk['percent'] if disk else 'N/A'}%. "
            f"Uptime: {uptime['formatted']}."
        ),
        "metrics": {
            "cpu": {
                "utilization_percent": cpu_percent,
            },
            "memory": memory,
            "disk": disk,
            "uptime": uptime,
            "services": services,
        },
        "findings": findings,
    }
