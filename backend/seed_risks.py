from backend.config.database import SessionLocal
from backend.models.risk import Risk
from backend.models.vulnerability import Vulnerability
from backend.models.asset import Asset
from backend.services.risk_engine import calculate_risk_score


THREATS = {
    "HIGH": [
        "Unauthorized access",
        "Privilege escalation",
        "Remote exploitation",
        "Credential compromise",
    ],
    "MEDIUM": [
        "Service disruption",
        "Unauthorized activity",
        "Configuration abuse",
        "Information disclosure",
    ],
    "LOW": [
        "Limited information disclosure",
        "Configuration misuse",
        "Low-impact unauthorized activity",
    ],
    "CRITICAL": [
        "System compromise",
        "Unauthorized privileged access",
        "Critical service compromise",
    ],
}


MITIGATIONS = {
    "HIGH": (
        "Apply security patches, enforce least privilege, "
        "strengthen authentication controls and monitor "
        "related security events."
    ),
    "MEDIUM": (
        "Review the affected configuration, apply appropriate "
        "hardening and maintain monitoring for recurrence."
    ),
    "LOW": (
        "Apply recommended hardening and monitor the affected "
        "asset during normal security operations."
    ),
    "CRITICAL": (
        "Immediately investigate the affected asset, apply "
        "critical remediation, restrict unnecessary access and "
        "maintain enhanced monitoring until resolved."
    ),
}


def select_threat(severity: str, index: int) -> str:
    threats = THREATS.get(
        severity,
        THREATS["MEDIUM"],
    )

    return threats[index % len(threats)]


def main():
    db = SessionLocal()

    try:
        vulnerabilities = (
            db.query(Vulnerability)
            .order_by(Vulnerability.id)
            .all()
        )

        if len(vulnerabilities) < 15:
            raise RuntimeError(
                f"Expected at least 15 vulnerabilities, "
                f"found {len(vulnerabilities)}."
            )

        created = 0
        updated = 0

        for index, vulnerability in enumerate(
            vulnerabilities[:15],
            start=1,
        ):
            asset = (
                db.query(Asset)
                .filter(
                    Asset.id ==
                    vulnerability.asset_id
                )
                .first()
            )

            if not asset:
                raise RuntimeError(
                    f"Asset {vulnerability.asset_id} "
                    f"not found for vulnerability "
                    f"{vulnerability.id}."
                )

            severity = (
                vulnerability.severity or
                vulnerability.risk_level or
                "MEDIUM"
            )

            # Controlled assessment values.
            likelihood = {
                "LOW": 2,
                "MEDIUM": 3,
                "HIGH": 4,
                "CRITICAL": 5,
            }.get(
                severity,
                3,
            )

            impact = {
                "LOW": 2,
                "MEDIUM": 3,
                "HIGH": 4,
                "CRITICAL": 5,
            }.get(
                severity,
                3,
            )

            calculation = calculate_risk_score(
                likelihood=likelihood,
                impact=impact,
                asset_criticality=asset.criticality,
                vulnerability_severity=severity,
            )

            risk_id = (
                f"RISK-2026-{index:03d}"
            )

            threat = select_threat(
                severity,
                index - 1,
            )

            vulnerability_description = (
                getattr(
                    vulnerability,
                    "description",
                    None,
                )
                or
                getattr(
                    vulnerability,
                    "title",
                    None,
                )
                or
                f"Security vulnerability "
                f"{getattr(vulnerability, 'vulnerability_id', vulnerability.id)}"
            )

            mitigation = MITIGATIONS.get(
                calculation["risk_level"],
                MITIGATIONS["MEDIUM"],
            )

            risk = (
                db.query(Risk)
                .filter(
                    Risk.risk_id == risk_id
                )
                .first()
            )

            if risk:
                updated += 1
            else:
                risk = Risk(
                    risk_id=risk_id,
                )
                db.add(risk)
                created += 1

            risk.asset_id = asset.id
            risk.vulnerability_id = (
                vulnerability.id
            )
            risk.threat = threat
            risk.vulnerability = (
                vulnerability_description
            )
            risk.likelihood = (
                calculation[
                    "effective_likelihood"
                ]
            )
            risk.impact = (
                calculation[
                    "effective_impact"
                ]
            )
            risk.risk_score = (
                calculation["score"]
            )
            risk.risk_level = (
                calculation["risk_level"]
            )
            risk.mitigation = mitigation

            # Keep the existing historical risk closed;
            # newly generated risks remain open.
            if risk.id == 1:
                risk.status = "CLOSED"
            else:
                risk.status = "OPEN"

        db.commit()

        total = (
            db.query(Risk).count()
        )

        print(
            f"Created: {created}"
        )
        print(
            f"Updated: {updated}"
        )
        print(
            f"Total risks: {total}"
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
