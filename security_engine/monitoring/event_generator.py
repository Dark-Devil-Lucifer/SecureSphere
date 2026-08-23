import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


BASE_URL = "http://127.0.0.1:8000"

USERNAME = os.getenv("SECURESPHERE_USERNAME", "admin")
PASSWORD = os.getenv("SECURESPHERE_PASSWORD")


EVENTS = [

    {
        "asset_id": 2,
        "source": "auth.log",
        "event_type": "FAILED_LOGIN",
        "category": "AUTHENTICATION",
        "severity": "MEDIUM",
        "description":
            "Failed SSH authentication attempt for an invalid user.",
        "raw_data":
            "sshd: Failed password for invalid user test"
    },

    {
        "asset_id": 2,
        "source": "auth.log",
        "event_type": "FAILED_LOGIN",
        "category": "AUTHENTICATION",
        "severity": "MEDIUM",
        "description":
            "Repeated failed SSH authentication detected.",
        "raw_data":
            "sshd: Failed password for invalid user admin"
    },

    {
        "asset_id": 1,
        "source": "auth.log",
        "event_type": "FAILED_LOGIN",
        "category": "AUTHENTICATION",
        "severity": "HIGH",
        "description":
            "Multiple authentication failures detected against security lab.",
        "raw_data":
            "sshd: authentication failure"
    },

    {
        "asset_id": 3,
        "source": "auth.log",
        "event_type": "SUCCESSFUL_LOGIN",
        "category": "AUTHENTICATION",
        "severity": "INFORMATIONAL",
        "description":
            "Successful user authentication.",
        "raw_data":
            "sshd: Accepted password"
    },

    {
        "asset_id": 4,
        "source": "mysql.log",
        "event_type": "DATABASE_LOGIN_FAILURE",
        "category": "AUTHENTICATION",
        "severity": "HIGH",
        "description":
            "Repeated failed database authentication attempt.",
        "raw_data":
            "Access denied for user"
    },

    {
        "asset_id": 5,
        "source": "systemd",
        "event_type": "SERVICE_STOPPED",
        "category": "SYSTEM",
        "severity": "HIGH",
        "description":
            "Security monitoring service unexpectedly stopped.",
        "raw_data":
            "systemd: service entered failed state"
    },

    {
        "asset_id": 6,
        "source": "systemd",
        "event_type": "SERVICE_RESTARTED",
        "category": "SYSTEM",
        "severity": "MEDIUM",
        "description":
            "Log collection service restarted.",
        "raw_data":
            "systemd: service restarted successfully"
    },

    {
        "asset_id": 7,
        "source": "application.log",
        "event_type": "APPLICATION_ERROR",
        "category": "APPLICATION",
        "severity": "MEDIUM",
        "description":
            "Application generated an unexpected internal error.",
        "raw_data":
            "HTTP 500 Internal Server Error"
    },

    {
        "asset_id": 7,
        "source": "application.log",
        "event_type": "AUTHENTICATION_BYPASS_ATTEMPT",
        "category": "SECURITY_ALERT",
        "severity": "CRITICAL",
        "description":
            "Possible authentication bypass attempt detected.",
        "raw_data":
            "Suspicious authentication parameter detected"
    },

    {
        "asset_id": 8,
        "source": "firewall.log",
        "event_type": "BLOCKED_CONNECTION",
        "category": "NETWORK",
        "severity": "MEDIUM",
        "description":
            "Firewall blocked a connection from an untrusted source.",
        "raw_data":
            "Firewall DROP packet"
    },

    {
        "asset_id": 8,
        "source": "firewall.log",
        "event_type": "PORT_SCAN",
        "category": "NETWORK",
        "severity": "HIGH",
        "description":
            "Multiple ports scanned from a single source.",
        "raw_data":
            "Multiple connection attempts detected"
    },

    {
        "asset_id": 9,
        "source": "sudo.log",
        "event_type": "PRIVILEGED_COMMAND",
        "category": "PERMISSION",
        "severity": "HIGH",
        "description":
            "Privileged command executed using sudo.",
        "raw_data":
            "sudo: command executed"
    },

    {
        "asset_id": 9,
        "source": "audit.log",
        "event_type": "PERMISSION_CHANGE",
        "category": "PERMISSION",
        "severity": "HIGH",
        "description":
            "File permissions were modified on a security-sensitive resource.",
        "raw_data":
            "chmod permission change detected"
    },

    {
        "asset_id": 10,
        "source": "kernel.log",
        "event_type": "HIGH_CPU_USAGE",
        "category": "SYSTEM",
        "severity": "MEDIUM",
        "description":
            "CPU utilization exceeded the configured monitoring threshold.",
        "raw_data":
            "CPU utilization exceeded 90 percent"
    },

    {
        "asset_id": 10,
        "source": "kernel.log",
        "event_type": "MEMORY_WARNING",
        "category": "SYSTEM",
        "severity": "MEDIUM",
        "description":
            "System memory utilization reached a warning threshold.",
        "raw_data":
            "Memory utilization exceeded threshold"
    },

    {
        "asset_id": 11,
        "source": "backup.log",
        "event_type": "BACKUP_FAILURE",
        "category": "APPLICATION",
        "severity": "HIGH",
        "description":
            "Scheduled backup operation failed.",
        "raw_data":
            "Backup job exited with error"
    },

    {
        "asset_id": 4,
        "source": "database.log",
        "event_type": "SUSPICIOUS_QUERY",
        "category": "SECURITY_ALERT",
        "severity": "HIGH",
        "description":
            "Database query matched suspicious activity indicators.",
        "raw_data":
            "Suspicious SQL pattern detected"
    },

    {
        "asset_id": 5,
        "source": "security.log",
        "event_type": "MALWARE_SIGNATURE",
        "category": "SECURITY_ALERT",
        "severity": "CRITICAL",
        "description":
            "Test malware signature detected in the controlled lab.",
        "raw_data":
            "Controlled test signature detected"
    },

    {
        "asset_id": 6,
        "source": "network.log",
        "event_type": "UNUSUAL_TRAFFIC",
        "category": "NETWORK",
        "severity": "HIGH",
        "description":
            "Unusual outbound traffic volume detected.",
        "raw_data":
            "Outbound traffic exceeded baseline"
    },

    {
        "asset_id": 1,
        "source": "audit.log",
        "event_type": "SECURITY_CONFIGURATION_CHANGE",
        "category": "SECURITY_ALERT",
        "severity": "CRITICAL",
        "description":
            "Security configuration was modified.",
        "raw_data":
            "Security configuration change detected"
    },

]


def login():

    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "username": USERNAME,
            "password": PASSWORD
        },
        timeout=10
    )

    response.raise_for_status()

    return response.json()["access_token"]


def generate_events():

    token = login()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    base_time = datetime.now()

    created = 0

    for index, event in enumerate(EVENTS, start=2):

        payload = {
            "event_id":
                f"EVT-2026-{index:03d}",

            "asset_id":
                event["asset_id"],

            "event_timestamp":
                (
                    base_time -
                    timedelta(minutes=index)
                ).isoformat(),

            "source":
                event["source"],

            "event_type":
                event["event_type"],

            "category":
                event["category"],

            "severity":
                event["severity"],

            "description":
                event["description"],

            "raw_data":
                event["raw_data"]
        }

        response = requests.post(
            f"{BASE_URL}/api/security-events",
            json=payload,
            headers=headers,
            timeout=10
        )

        if response.status_code == 201:

            print(
                f"[+] Created "
                f"{payload['event_id']} "
                f"{payload['event_type']}"
            )

            created += 1

        else:

            print(
                f"[!] Failed "
                f"{payload['event_id']}: "
                f"{response.status_code} "
                f"{response.text}"
            )

    print()
    print(
        f"Created {created} test security events."
    )


if __name__ == "__main__":
    generate_events()
