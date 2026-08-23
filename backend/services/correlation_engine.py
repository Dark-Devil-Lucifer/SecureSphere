from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from backend.models.security_event import SecurityEvent
from backend.models.alert import Alert


FAILED_LOGIN_WINDOW_MINUTES = 5
FAILED_LOGIN_THRESHOLD = 4


def correlate_failed_login_spike(
    db: Session,
    event: SecurityEvent
):
    """
    Detect a burst of failed login attempts against
    the same asset within a five-minute window.

    Returns:
        Existing/new Alert when a correlation is triggered.
        None when the threshold is not reached.
    """

    if (
        (event.event_type or "").upper()
        != "FAILED_LOGIN"
    ):
        return None

    window_start = (
        event.event_timestamp
        - timedelta(
            minutes=FAILED_LOGIN_WINDOW_MINUTES
        )
    )

    failed_logins = (
        db.query(SecurityEvent)
        .filter(
            SecurityEvent.asset_id == event.asset_id,
            SecurityEvent.event_type == "FAILED_LOGIN",
            SecurityEvent.event_timestamp >= window_start,
            SecurityEvent.event_timestamp <= event.event_timestamp
        )
        .order_by(
            SecurityEvent.event_timestamp.asc()
        )
        .all()
    )

    if len(failed_logins) < FAILED_LOGIN_THRESHOLD:
        return None

    rule_name = "FAILED_LOGIN_SPIKE"

    # Prevent duplicate correlation alerts for
    # the same detection window.
    existing = (
        db.query(Alert)
        .filter(
            Alert.asset_id == event.asset_id,
            Alert.rule_name == rule_name,
            Alert.trigger_time >= window_start,
            Alert.trigger_time <= event.event_timestamp
        )
        .first()
    )

    if existing:
        return existing

    alert_id = (
        f"ALT-CORR-{event.id:04d}"
    )

    existing_id = (
        db.query(Alert)
        .filter(
            Alert.alert_id == alert_id
        )
        .first()
    )

    if existing_id:
        return existing_id

    alert = Alert(
        alert_id=alert_id,
        event_id=event.id,
        asset_id=event.asset_id,
        rule_name=rule_name,
        title="Multiple Failed Login Attempts Detected",
        severity="HIGH",
        trigger_time=event.event_timestamp,
        description=(
            f"{len(failed_logins)} failed login attempts "
            f"were detected against the same asset within "
            f"{FAILED_LOGIN_WINDOW_MINUTES} minutes."
        ),
        status="NEW",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )    

    db.add(alert)
    db.flush()

    return alert
