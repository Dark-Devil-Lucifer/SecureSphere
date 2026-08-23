from datetime import datetime
import json

from sqlalchemy.orm import Session

from backend.models.asset import Asset
from backend.models.alert import Alert
from backend.models.incident import Incident
from backend.models.risk import Risk
from backend.models.vulnerability import Vulnerability
from backend.services.posture_score import (
    calculate_posture_score,
)

AUTOMATION_NAME = "SECURITY_HEALTH_CHECK"


def run_security_health_check(db: Session):
    """
    Evaluate the current security posture of SecureSphere.

    Returns a structured health-check result.
    """

    total_assets = db.query(Asset).count()

    active_assets = (
        db.query(Asset)
        .filter(Asset.status == "ACTIVE")
        .count()
    )

    critical_alerts = (
        db.query(Alert)
        .filter(
            Alert.severity == "CRITICAL",
            Alert.status != "RESOLVED"
        )
        .count()
    )

    high_alerts = (
        db.query(Alert)
        .filter(
            Alert.severity == "HIGH",
            Alert.status != "RESOLVED"
        )
        .count()
    )

    open_incidents = (
        db.query(Incident)
        .filter(
            Incident.status.in_(
                [
                    "OPEN",
                    "INVESTIGATING",
                    "CONTAINED",
                ]
            )
        )
        .count()
    )

    critical_incidents = (
        db.query(Incident)
        .filter(
            Incident.severity == "CRITICAL",
            Incident.status.in_(
                [
                    "OPEN",
                    "INVESTIGATING",
                    "CONTAINED",
                ]
            )
        )
        .count()
    )

    high_vulnerabilities = (
        db.query(Vulnerability)
        .filter(
            Vulnerability.severity.in_(
                ["CRITICAL", "HIGH"]
            ),
            Vulnerability.status != "RESOLVED"
        )
        .count()
    )

    open_high_risks = (
        db.query(Risk)
        .filter(
            Risk.risk_level.in_(
                ["CRITICAL", "HIGH"]
            ),
            Risk.status == "OPEN"
        )
        .count()
    )

    findings = []

    if critical_alerts > 0:
        findings.append(
            f"{critical_alerts} unresolved critical alert(s) detected."
        )

    if high_alerts > 0:
        findings.append(
            f"{high_alerts} unresolved high-severity alert(s) detected."
        )

    if critical_incidents > 0:
        findings.append(
            f"{critical_incidents} unresolved critical incident(s) detected."
        )

    if high_vulnerabilities > 0:
        findings.append(
            f"{high_vulnerabilities} unresolved critical/high vulnerability(ies) detected."
        )

    if open_high_risks > 0:
        findings.append(
            f"{open_high_risks} open critical/high risk(s) detected."
        )

    if total_assets == 0:
        health_status = "CRITICAL"
        findings.append("No monitored assets are configured.")

    elif critical_alerts > 0 or critical_incidents > 0:
        health_status = "CRITICAL"

    elif (
        high_alerts > 0
        or high_vulnerabilities > 0
        or open_high_risks > 0
    ):
        health_status = "WARNING"

    else:
        health_status = "HEALTHY"

    posture = calculate_posture_score(
        total_assets=total_assets,
        active_assets=active_assets,
        critical_alerts=critical_alerts,
        high_alerts=high_alerts,
        open_incidents=open_incidents,
        critical_incidents=critical_incidents,
        high_vulnerabilities=high_vulnerabilities,
        open_high_risks=open_high_risks,
    )

    return {

        "automation_name": AUTOMATION_NAME,
        "execution_time": datetime.utcnow().isoformat(),
        "status": health_status,
	"security_score": posture.score,
        "score_status": posture.status,
        "score_components": posture.components,
        "summary": (
            f"Security health status: {health_status}. "
            f"Monitored assets: {active_assets}/{total_assets}. "
            f"Open incidents: {open_incidents}. "
            f"Critical alerts: {critical_alerts}. "
            f"High alerts: {high_alerts}."
        ),
        "metrics": {
            "total_assets": total_assets,
            "active_assets": active_assets,
            "critical_alerts": critical_alerts,
            "high_alerts": high_alerts,
            "open_incidents": open_incidents,
            "critical_incidents": critical_incidents,
            "high_vulnerabilities": high_vulnerabilities,
            "open_high_risks": open_high_risks,
        },
        "findings": findings,
    }
