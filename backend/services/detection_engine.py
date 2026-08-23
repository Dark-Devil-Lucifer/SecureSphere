from datetime import datetime

from sqlalchemy.orm import Session

from backend.models.security_event import SecurityEvent
from backend.models.alert import Alert
from backend.services.incident_engine import (
    generate_incident_for_alert
)

def generate_alert_for_event(
    db: Session,
    event: SecurityEvent
):
    """
    Evaluate a security event and create an alert
    when the event matches a supported detection rule.

    Returns:
        Alert object if an alert is created.
        None if no rule is triggered.
    """

    event_type = (
        event.event_type or ""
    ).upper()

    severity = (
        event.severity or ""
    ).upper()

    rule_name = None
    title = None
    alert_severity = severity
    description = None

    # -------------------------------------------------
    # Unauthorized access / authentication bypass
    # -------------------------------------------------

    if event_type == "AUTHENTICATION_BYPASS_ATTEMPT":

        rule_name = "UNAUTHORIZED_ACCESS_ATTEMPT"

        title = (
            "Unauthorized Access Attempt Detected"
        )

        description = (
            "An authentication bypass attempt "
            "was detected against the monitored asset."
        )

        alert_severity = "CRITICAL"

    # -------------------------------------------------
    # Suspicious system activity
    # -------------------------------------------------

    elif event_type in {
        "SUSPICIOUS_QUERY",
        "UNUSUAL_TRAFFIC",
    }:

        rule_name = "SUSPICIOUS_SYSTEM_ACTIVITY"

        title = (
            "Suspicious System Activity Detected"
        )

        description = (
            "Suspicious system or application "
            "activity was detected on the monitored asset."
        )

        alert_severity = severity

    # -------------------------------------------------
    # Critical security event
    # -------------------------------------------------

    elif severity == "CRITICAL":

        rule_name = "CRITICAL_SECURITY_EVENT"

        title = (
            "Critical Security Event Detected"
        )

        description = (
            "A critical-severity security event "
            "was detected."
        )
    # -------------------------------------------------
    # Unauthorized access / authentication bypass
    # -------------------------------------------------

    elif event_type == "AUTHENTICATION_BYPASS_ATTEMPT":

        rule_name = "UNAUTHORIZED_ACCESS_ATTEMPT"

        title = (
            "Unauthorized Access Attempt Detected"
        )

        description = (
            "An authentication bypass attempt was "
            "detected against the monitored asset."
        )

        alert_severity = "CRITICAL"

    # -------------------------------------------------
    # Suspicious system activity
    # -------------------------------------------------

    elif event_type in {
        "SUSPICIOUS_QUERY",
        "UNUSUAL_TRAFFIC",
        "MALWARE_SIGNATURE",
    }:

        rule_name = "SUSPICIOUS_SYSTEM_ACTIVITY"

        title = (
            "Suspicious System Activity Detected"
        )

        description = (
            "Suspicious system or application activity "
            "was detected on the monitored asset."
        )

        alert_severity = severity

    # -------------------------------------------------
    # Network scan detection
    # -------------------------------------------------

    elif event_type == "FAILED_LOGIN":

        rule_name = "FAILED_LOGIN_ATTEMPT"

        title = (
            "Failed Login Attempt Detected"
        )

        description = (
            "A failed authentication attempt "
            "was detected against the monitored asset."
        )

        alert_severity = "MEDIUM"

    elif event_type == "PORT_SCAN":

        rule_name = "NETWORK_SCAN_DETECTION"

        title = (
            "Potential Network Scan Detected"
        )

        description = (
            "A network port scanning activity "
            "was detected."
        )

    # -------------------------------------------------
    # Privileged activity
    # -------------------------------------------------

    elif event_type in {
        "PRIVILEGED_COMMAND",
        "PERMISSION_CHANGE",
    }:

        rule_name = "PRIVILEGED_ACTIVITY"

        title = (
            "Privileged Activity Detected"
        )

        description = (
            "A privileged command or permission "
            "change was detected."
        )

    # -------------------------------------------------
    # Service failure
    # -------------------------------------------------

    elif event_type == "SERVICE_STOPPED":

        rule_name = "SERVICE_FAILURE"

        title = (
            "Security Service Failure"
        )

        description = (
            "A monitored service unexpectedly "
            "stopped."
        )

    # -------------------------------------------------
    # No matching rule
    # -------------------------------------------------

    else:

        return None

    # -------------------------------------------------
    # Prevent duplicate alert for the same event/rule
    # -------------------------------------------------

    existing = (
        db.query(Alert)
        .filter(
            Alert.event_id == event.id,
            Alert.rule_name == rule_name
        )
        .first()
    )

    if existing:

        return existing

    # -------------------------------------------------
    # Generate alert ID
    # -------------------------------------------------

    alert_id = (
        f"ALT-{datetime.utcnow().strftime('%Y')}"
        f"-{event.id:04d}"
    )

    existing_id = (
        db.query(Alert)
        .filter(
            Alert.alert_id == alert_id
        )
        .first()
    )

    if existing_id:

        alert_id = (
            f"ALT-{datetime.utcnow().strftime('%Y')}"
            f"-{event.id:04d}-1"
        )

    # -------------------------------------------------
    # Create alert
    # -------------------------------------------------

    alert = Alert(

        alert_id=alert_id,

        event_id=event.id,

        asset_id=event.asset_id,

        rule_name=rule_name,

        title=title,

        severity=alert_severity,

        trigger_time=event.event_timestamp,

        description=description,

        status="NEW",

        created_at=datetime.utcnow(),

        updated_at=datetime.utcnow(),

    )

    db.add(alert)

    db.flush()
    generate_incident_for_alert(
    	db,
    	alert
    )

    return alert
