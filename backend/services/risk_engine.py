from typing import Optional


LEVEL_FACTORS = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 4,
    "CRITICAL": 5,
}


def level_factor(level: Optional[str]) -> int:
    """
    Convert asset/vulnerability severity into a 1-5 risk factor.
    """
    if not level:
        return 1

    return LEVEL_FACTORS.get(
        str(level).upper(),
        1,
    )


def calculate_risk_score(
    likelihood: int,
    impact: int,
    asset_criticality: str,
    vulnerability_severity: Optional[str] = None,
) -> dict:
    """
    Calculate a 1-25 risk score using:

    - user-supplied likelihood
    - user-supplied impact
    - asset criticality
    - vulnerability severity

    The asset/vulnerability factors act as minimum effective
    likelihood/impact values so that high-criticality conditions
    cannot be understated.
    """

    asset_factor = level_factor(
        asset_criticality
    )

    vulnerability_factor = level_factor(
        vulnerability_severity
    )

    effective_likelihood = max(
        likelihood,
        asset_factor,
        vulnerability_factor,
    )

    effective_impact = max(
        impact,
        asset_factor,
        vulnerability_factor,
    )

    score = (
        effective_likelihood *
        effective_impact
    )

    if score >= 20:
        risk_level = "CRITICAL"
    elif score >= 12:
        risk_level = "HIGH"
    elif score >= 6:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "score": score,
        "risk_level": risk_level,
        "effective_likelihood": effective_likelihood,
        "effective_impact": effective_impact,
        "asset_factor": asset_factor,
        "vulnerability_factor": vulnerability_factor,
    }
