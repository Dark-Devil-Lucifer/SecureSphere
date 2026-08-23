from dataclasses import dataclass


@dataclass
class PostureScore:
    score: int
    status: str
    components: dict


def calculate_posture_score(
    total_assets: int,
    active_assets: int,
    critical_alerts: int,
    high_alerts: int,
    open_incidents: int,
    critical_incidents: int,
    high_vulnerabilities: int,
    open_high_risks: int,
) -> PostureScore:
    """
    Calculate a database-driven SecureSphere security posture
    score from 0 to 100.

    100 = strongest posture.
    0   = weakest posture.

    The score starts at 100 and applies bounded penalties
    for unresolved security conditions.

    Component weights:

    - Alerts:          25 points
    - Incidents:       25 points
    - Vulnerabilities: 25 points
    - Risks:            20 points
    - Asset health:      5 points

    All penalties are capped so the final score always remains
    between 0 and 100.
    """

    # ---------------------------------------------------------
    # ALERT PENALTY — maximum 25 points
    # ---------------------------------------------------------

    alert_penalty = min(
        25,
        (critical_alerts * 3)
        + (high_alerts * 1),
    )

    # ---------------------------------------------------------
    # INCIDENT PENALTY — maximum 25 points
    # ---------------------------------------------------------

    incident_penalty = min(
        25,
        (critical_incidents * 5)
        + (max(open_incidents - critical_incidents, 0) * 2),
    )

    # ---------------------------------------------------------
    # VULNERABILITY PENALTY — maximum 25 points
    # ---------------------------------------------------------

    vulnerability_penalty = min(
        25,
        high_vulnerabilities * 3,
    )

    # ---------------------------------------------------------
    # RISK PENALTY — maximum 20 points
    # ---------------------------------------------------------

    risk_penalty = min(
        20,
        open_high_risks * 4,
    )

    # ---------------------------------------------------------
    # ASSET HEALTH — maximum 5 points
    # ---------------------------------------------------------

    if total_assets == 0:
        asset_penalty = 5

    else:
        inactive_assets = max(
            total_assets - active_assets,
            0,
        )

        inactive_ratio = (
            inactive_assets / total_assets
        )

        asset_penalty = min(
            5,
            round(inactive_ratio * 5),
        )

    total_penalty = (
        alert_penalty
        + incident_penalty
        + vulnerability_penalty
        + risk_penalty
        + asset_penalty
    )

    score = max(
        0,
        min(
            100,
            100 - total_penalty,
        ),
    )

    # ---------------------------------------------------------
    # STATUS CLASSIFICATION
    # ---------------------------------------------------------

    if score >= 80:
        status = "HEALTHY"

    elif score >= 60:
        status = "WARNING"

    else:
        status = "CRITICAL"

    return PostureScore(
        score=score,
        status=status,
        components={
            "alert_penalty": alert_penalty,
            "incident_penalty": incident_penalty,
            "vulnerability_penalty": vulnerability_penalty,
            "risk_penalty": risk_penalty,
            "asset_penalty": asset_penalty,
            "total_penalty": total_penalty,
        },
    )
