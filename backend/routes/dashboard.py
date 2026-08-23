from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.config.database import get_db

from backend.models.asset import Asset
from backend.models.vulnerability import Vulnerability
from backend.models.security_event import SecurityEvent
from backend.models.alert import Alert
from backend.models.incident import Incident
from backend.models.risk import Risk
from backend.models.assessment import Assessment
from backend.models.user import User

from backend.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


@router.get("/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # =====================================================
    # ASSETS
    # =====================================================

    total_assets = (
        db.query(func.count(Asset.id))
        .scalar()
    )

    active_assets = (
        db.query(func.count(Asset.id))
        .filter(Asset.status == "ACTIVE")
        .scalar()
    )

    inactive_assets = (
        db.query(func.count(Asset.id))
        .filter(Asset.status == "INACTIVE")
        .scalar()
    )

    retired_assets = (
        db.query(func.count(Asset.id))
        .filter(Asset.status == "RETIRED")
        .scalar()
    )

    critical_assets = (
        db.query(func.count(Asset.id))
        .filter(Asset.criticality == "CRITICAL")
        .scalar()
    )

    high_assets = (
        db.query(func.count(Asset.id))
        .filter(Asset.criticality == "HIGH")
        .scalar()
    )

    medium_assets = (
        db.query(func.count(Asset.id))
        .filter(Asset.criticality == "MEDIUM")
        .scalar()
    )

    low_assets = (
        db.query(func.count(Asset.id))
        .filter(Asset.criticality == "LOW")
        .scalar()
    )


    # =====================================================
    # VULNERABILITIES
    # =====================================================

    total_vulnerabilities = (
        db.query(func.count(Vulnerability.id))
        .scalar()
    )

    critical_vulnerabilities = (
        db.query(func.count(Vulnerability.id))
        .filter(
            Vulnerability.severity == "CRITICAL"
        )
        .scalar()
    )

    high_vulnerabilities = (
        db.query(func.count(Vulnerability.id))
        .filter(
            Vulnerability.severity == "HIGH"
        )
        .scalar()
    )


    # =====================================================
    # SECURITY EVENTS
    # =====================================================

    total_security_events = (
        db.query(func.count(SecurityEvent.id))
        .scalar()
    )

    critical_security_events = (
        db.query(func.count(SecurityEvent.id))
        .filter(
            SecurityEvent.severity == "CRITICAL"
        )
        .scalar()
    )

    open_security_events = (
        db.query(func.count(SecurityEvent.id))
        .filter(
            SecurityEvent.status.in_(
                ["NEW", "INVESTIGATING"]
            )
        )
        .scalar()
    )


    # =====================================================
    # ALERTS
    # =====================================================

    total_alerts = (
        db.query(func.count(Alert.id))
        .scalar()
    )

    critical_alerts = (
        db.query(func.count(Alert.id))
        .filter(
            Alert.severity == "CRITICAL"
        )
        .scalar()
    )

    high_alerts = (
        db.query(func.count(Alert.id))
        .filter(
            Alert.severity == "HIGH"
        )
        .scalar()
    )

    new_alerts = (
        db.query(func.count(Alert.id))
        .filter(
            Alert.status == "NEW"
        )
        .scalar()
    )


    # =====================================================
    # INCIDENTS
    # =====================================================

    total_incidents = (
        db.query(func.count(Incident.id))
        .scalar()
    )

    open_incidents = (
        db.query(func.count(Incident.id))
        .filter(
            Incident.status == "OPEN"
        )
        .scalar()
    )

    investigating_incidents = (
        db.query(func.count(Incident.id))
        .filter(
            Incident.status == "INVESTIGATING"
        )
        .scalar()
    )

    critical_incidents = (
        db.query(func.count(Incident.id))
        .filter(
            Incident.severity == "CRITICAL"
        )
        .scalar()
    )


    # =====================================================
    # RISKS
    # =====================================================

    total_risks = (
        db.query(func.count(Risk.id))
        .scalar()
    )

    critical_risks = (
        db.query(func.count(Risk.id))
        .filter(
            Risk.risk_level == "CRITICAL"
        )
        .scalar()
    )

    high_risks = (
        db.query(func.count(Risk.id))
        .filter(
            Risk.risk_level == "HIGH"
        )
        .scalar()
    )

    open_risks = (
        db.query(func.count(Risk.id))
        .filter(
            Risk.status == "OPEN"
        )
        .scalar()
    )


    # =====================================================
    # ASSESSMENTS
    # =====================================================

    total_assessments = (
        db.query(func.count(Assessment.id))
        .scalar()
    )

    planned_assessments = (
        db.query(func.count(Assessment.id))
        .filter(
            Assessment.status == "PLANNED"
        )
        .scalar()
    )

    in_progress_assessments = (
        db.query(func.count(Assessment.id))
        .filter(
            Assessment.status == "IN_PROGRESS"
        )
        .scalar()
    )

    completed_assessments = (
        db.query(func.count(Assessment.id))
        .filter(
            Assessment.status == "COMPLETED"
        )
        .scalar()
    )


    # =====================================================
    # RESPONSE
    # =====================================================

    return {

        "assets": {
            "total": total_assets,
            "active": active_assets,
            "inactive": inactive_assets,
            "retired": retired_assets
        },

        "criticality": {
            "critical": critical_assets,
            "high": high_assets,
            "medium": medium_assets,
            "low": low_assets
        },

        "vulnerabilities": {
            "total": total_vulnerabilities,
            "critical": critical_vulnerabilities,
            "high": high_vulnerabilities
        },

        "security_events": {
            "total": total_security_events,
            "critical": critical_security_events,
            "open": open_security_events
        },

        "alerts": {
            "total": total_alerts,
            "critical": critical_alerts,
            "high": high_alerts,
            "new": new_alerts
        },

        "incidents": {
            "total": total_incidents,
            "open": open_incidents,
            "investigating": investigating_incidents,
            "critical": critical_incidents
        },

        "risks": {
            "total": total_risks,
            "critical": critical_risks,
            "high": high_risks,
            "open": open_risks
        },

        "assessments": {
            "total": total_assessments,
            "planned": planned_assessments,
            "in_progress": in_progress_assessments,
            "completed": completed_assessments
        },

        "user": {
            "username": current_user.username,
            "role": current_user.role
        }
    }
