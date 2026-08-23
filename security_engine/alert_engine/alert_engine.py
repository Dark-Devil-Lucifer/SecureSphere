from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from backend.config.database import SessionLocal

# Import all ORM models so SQLAlchemy can
# resolve relationships when running the
# alert engine as a standalone module.
from backend.models import (
    User,
    Asset,
    Assessment,
    Vulnerability,
    SecurityEvent,
    Alert,
)

def create_alert(
    db: Session,
    event: SecurityEvent,
    rule_name: str,
    title: str,
    severity: str,
    description: str,
):

    existing = db.query(
        Alert
    ).filter(
        Alert.event_id == event.id,
        Alert.rule_name == rule_name
    ).first()


    if existing:

        return False


    alert = Alert(

        alert_id=(
            f"ALT-2026-"
            f"{event.id:04d}-"
            f"{abs(hash(rule_name)) % 1000:03d}"
        ),

        event_id=event.id,

        asset_id=event.asset_id,

        rule_name=rule_name,

        title=title,

        severity=severity,

        trigger_time=event.event_timestamp,

        description=description,

        status="NEW",

        created_at=datetime.utcnow(),

        updated_at=datetime.utcnow(),

    )


    db.add(alert)

    return True


def run_alert_engine():

    db = SessionLocal()

    created = 0


    try:

        events = (
            db.query(SecurityEvent)
            .order_by(
                SecurityEvent.id.asc()
            )
            .all()
        )


        for event in events:

            # -------------------------------------------------
            # RULE 1 — Critical Security Event
            # -------------------------------------------------

            if event.severity == "CRITICAL":

                if create_alert(

                    db,

                    event,

                    "CRITICAL_SECURITY_EVENT",

                    "Critical Security Event Detected",

                    "CRITICAL",

                    (
                        "A critical-severity "
                        "security event was detected."
                    ),

                ):

                    created += 1


            # -------------------------------------------------
            # RULE 2 — Network Scan Detection
            # -------------------------------------------------

            if event.event_type == "PORT_SCAN":

                if create_alert(

                    db,

                    event,

                    "NETWORK_SCAN_DETECTION",

                    "Potential Network Scan Detected",

                    "HIGH",

                    (
                        "A network port scanning "
                        "activity was detected."
                    ),

                ):

                    created += 1


            # -------------------------------------------------
            # RULE 3 — Privileged Activity
            # -------------------------------------------------

            if event.event_type in {

                "PRIVILEGED_COMMAND",

                "PERMISSION_CHANGE",

            }:

                if create_alert(

                    db,

                    event,

                    "PRIVILEGED_ACTIVITY",

                    "Privileged Activity Detected",

                    "HIGH",

                    (
                        "A privileged command or "
                        "permission change was detected."
                    ),

                ):

                    created += 1


            # -------------------------------------------------
            # RULE 4 — Service Failure
            # -------------------------------------------------

            if event.event_type == "SERVICE_STOPPED":

                if create_alert(

                    db,

                    event,

                    "SERVICE_FAILURE",

                    "Security Service Failure",

                    "HIGH",

                    (
                        "A monitored service "
                        "unexpectedly stopped."
                    ),

                ):

                    created += 1


        # -----------------------------------------------------
        # RULE 5 — Brute Force Detection
        # -----------------------------------------------------

        authentication_events = (

            db.query(SecurityEvent)

            .filter(

                SecurityEvent.category
                == "AUTHENTICATION",

                SecurityEvent.event_type
                == "FAILED_LOGIN",

            )

            .order_by(
                SecurityEvent.event_timestamp.asc()
            )

            .all()

        )


        for event in authentication_events:

            window_start = (
                event.event_timestamp
                - timedelta(minutes=10)
            )


            failed_count = (

                db.query(SecurityEvent)

                .filter(

                    SecurityEvent.asset_id
                    == event.asset_id,

                    SecurityEvent.category
                    == "AUTHENTICATION",

                    SecurityEvent.event_type
                    == "FAILED_LOGIN",

                    SecurityEvent.event_timestamp
                    >= window_start,

                    SecurityEvent.event_timestamp
                    <= event.event_timestamp,

                )

                .count()

            )


            if failed_count >= 3:

                if create_alert(

                    db,

                    event,

                    "BRUTE_FORCE_DETECTION",

                    "Potential Brute Force Activity",

                    "HIGH",

                    (
                        f"{failed_count} failed "
                        "authentication attempts "
                        "were detected within "
                        "a 10-minute window."
                    ),

                ):

                    created += 1


        db.commit()


        print(
            f"Alert engine completed. "
            f"Created {created} new alerts."
        )


    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


if __name__ == "__main__":

    run_alert_engine()
