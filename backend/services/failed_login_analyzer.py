from collections import defaultdict
from datetime import timedelta

from sqlalchemy.orm import Session

from backend.models.security_event import SecurityEvent


AUTOMATION_NAME = "FAILED_LOGIN_ANALYZER"

FAILED_LOGIN_WINDOW_MINUTES = 5
FAILED_LOGIN_THRESHOLD = 4


def run_failed_login_analyzer(db: Session):
    """
    Analyze authorized SecureSphere security events for
    failed authentication activity.

    The analyzer:
    - reads FAILED_LOGIN security events
    - counts failed login attempts
    - groups attempts by asset and source
    - identifies repeated attempts
    - detects five-minute login spikes
    - produces suspicious-pattern findings

    This module analyzes existing security events.
    Alert creation remains the responsibility of
    correlation_engine.py.
    """

    try:
        failed_logins = (
            db.query(SecurityEvent)
            .filter(
                SecurityEvent.event_type == "FAILED_LOGIN"
            )
            .order_by(
                SecurityEvent.event_timestamp.asc()
            )
            .all()
        )

        total_failed_logins = len(
            failed_logins
        )

        # -------------------------------------------------
        # Group failed logins by asset
        # -------------------------------------------------

        asset_counts = defaultdict(int)

        for event in failed_logins:
            asset_counts[event.asset_id] += 1

        # -------------------------------------------------
        # Group failed logins by source
        # -------------------------------------------------

        source_counts = defaultdict(int)

        for event in failed_logins:
            source = (
                event.source
                or "UNKNOWN"
            )

            source_counts[source] += 1

        # -------------------------------------------------
        # Detect repeated login attempts
        #
        # A source with two or more failed attempts
        # is considered repeated activity.
        # -------------------------------------------------

        repeated_sources = {
            source: count
            for source, count
            in source_counts.items()
            if count >= 2
        }

        # -------------------------------------------------
        # Detect five-minute spikes
        # -------------------------------------------------

        spike_findings = []

        for event in failed_logins:

            window_start = (
                event.event_timestamp
                - timedelta(
                    minutes=FAILED_LOGIN_WINDOW_MINUTES
                )
            )

            window_events = [
                candidate
                for candidate in failed_logins
                if (
                    candidate.asset_id
                    == event.asset_id
                    and
                    window_start
                    <= candidate.event_timestamp
                    <= event.event_timestamp
                )
            ]

            if len(window_events) >= FAILED_LOGIN_THRESHOLD:

                finding = {
                    "asset_id": event.asset_id,
                    "event_time": (
                        event.event_timestamp.isoformat()
                    ),
                    "attempt_count": len(
                        window_events
                    ),
                    "window_minutes":
                        FAILED_LOGIN_WINDOW_MINUTES,
                }

                if finding not in spike_findings:
                    spike_findings.append(
                        finding
                    )

        # -------------------------------------------------
        # Build findings
        # -------------------------------------------------

        findings = []

        if total_failed_logins > 0:
            findings.append(
                f"{total_failed_logins} failed "
                "login attempt(s) detected."
            )

        if repeated_sources:
            findings.append(
                f"{len(repeated_sources)} source(s) "
                "generated repeated failed-login activity."
            )

        if spike_findings:
            findings.append(
                f"{len(spike_findings)} failed-login "
                "spike(s) exceeded the configured "
                f"threshold of {FAILED_LOGIN_THRESHOLD} "
                f"attempts within "
                f"{FAILED_LOGIN_WINDOW_MINUTES} minutes."
            )

        # -------------------------------------------------
        # Determine analyzer status
        # -------------------------------------------------

        if spike_findings:
            status = "SUSPICIOUS"

        elif repeated_sources:
            status = "WARNING"

        else:
            status = "NORMAL"

        # -------------------------------------------------
        # Summary
        # -------------------------------------------------

        summary = (
            f"Failed Login Analyzer status: {status}. "
            f"Analyzed {total_failed_logins} failed "
            "login attempt(s) across "
            f"{len(asset_counts)} asset(s). "
            f"Detected {len(repeated_sources)} "
            "repeated source(s) and "
            f"{len(spike_findings)} suspicious "
            "spike(s)."
        )

        return {
            "automation_name": AUTOMATION_NAME,
            "status": status,
            "summary": summary,
            "metrics": {
                "total_failed_logins":
                    total_failed_logins,

                "affected_assets":
                    len(asset_counts),

                "unique_sources":
                    len(source_counts),

                "repeated_sources":
                    len(repeated_sources),

                "suspicious_spikes":
                    len(spike_findings),
            },
            "asset_counts": dict(
                asset_counts
            ),
            "source_counts": dict(
                source_counts
            ),
            "repeated_sources":
                dict(repeated_sources),

            "spike_findings":
                spike_findings,

            "findings":
                findings,
        }

    except Exception:
        raise
