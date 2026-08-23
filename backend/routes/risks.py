from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.models.risk import Risk
from backend.models.risk_schema import (
    RiskCreate,
    RiskResponse,
    RiskStatusUpdate,
)
from backend.models.asset import Asset
from backend.models.vulnerability import Vulnerability
from backend.services.risk_engine import (
    calculate_risk_score,
)
from backend.utils.dependencies import (
    get_current_user,
    require_roles,
)


router = APIRouter(
    prefix="/api/risks",
    tags=["Risk Assessment"],
)


@router.get(
    "",
    response_model=list[RiskResponse],
)
def get_risks(
    search: str | None = Query(
        default=None,
        description="Search by risk ID, threat, or vulnerability",
    ),
    risk_level: str | None = Query(
        default=None,
        description="Filter by risk level",
    ),
    status: str | None = Query(
        default=None,
        description="Filter by risk status",
    ),
    asset_id: int | None = Query(
        default=None,
        description="Filter by asset ID",
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Risk)

    # -----------------------------
    # Search
    # -----------------------------

    if search:
        search_value = f"%{search.strip()}%"

        query = query.filter(
            (
                Risk.risk_id.ilike(search_value)
                | Risk.threat.ilike(search_value)
                | Risk.vulnerability.ilike(search_value)
            )
        )

    # -----------------------------
    # Risk level
    # -----------------------------

    if risk_level:
        risk_level_value = risk_level.upper()

        allowed_levels = {
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL",
        }

        if risk_level_value not in allowed_levels:
            raise HTTPException(
                status_code=400,
                detail="Invalid risk level",
            )

        query = query.filter(
            Risk.risk_level == risk_level_value
        )

    # -----------------------------
    # Status
    # -----------------------------

    if status:
        status_value = status.upper()

        allowed_statuses = {
            "OPEN",
            "MITIGATED",
            "ACCEPTED",
            "CLOSED",
        }

        if status_value not in allowed_statuses:
            raise HTTPException(
                status_code=400,
                detail="Invalid risk status",
            )

        query = query.filter(
            Risk.status == status_value
        )

    # -----------------------------
    # Asset
    # -----------------------------

    if asset_id is not None:
        query = query.filter(
            Risk.asset_id == asset_id
        )

    return (
        query
        .order_by(Risk.id.desc())
        .all()
    )

@router.get(
    "/{risk_id}",
    response_model=RiskResponse,
)
def get_risk(
    risk_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    risk = (
        db.query(Risk)
        .filter(Risk.id == risk_id)
        .first()
    )

    if not risk:
        raise HTTPException(
            status_code=404,
            detail="Risk not found",
        )

    return risk


@router.post(
    "",
    response_model=RiskResponse,
    status_code=201,
)
def create_risk(
    risk_data: RiskCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "ADMIN",
            "SECURITY_ANALYST",
        )
    ),
):
    asset = (
        db.query(Asset)
        .filter(
            Asset.id == risk_data.asset_id
        )
        .first()
    )

    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Asset not found",
        )

    vulnerability = None

    if risk_data.vulnerability_id is not None:
        vulnerability = (
            db.query(Vulnerability)
            .filter(
                Vulnerability.id ==
                risk_data.vulnerability_id
            )
            .first()
        )

        if not vulnerability:
            raise HTTPException(
                status_code=404,
                detail="Vulnerability not found",
            )

    existing = (
        db.query(Risk)
        .filter(
            Risk.risk_id ==
            risk_data.risk_id
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Risk ID already exists",
        )

    calculation = calculate_risk_score(
        likelihood=risk_data.likelihood,
        impact=risk_data.impact,
        asset_criticality=asset.criticality,
        vulnerability_severity=(
            vulnerability.severity
            if vulnerability
            else None
        ),
    )

    risk = Risk(
        risk_id=risk_data.risk_id,
        asset_id=risk_data.asset_id,
        vulnerability_id=(
            risk_data.vulnerability_id
        ),
        threat=risk_data.threat,
        vulnerability=risk_data.vulnerability,
        likelihood=(
            calculation["effective_likelihood"]
        ),
        impact=(
            calculation["effective_impact"]
        ),
        risk_score=(
            calculation["score"]
        ),
        risk_level=(
            calculation["risk_level"]
        ),
        mitigation=risk_data.mitigation,
        status="OPEN",
    )

    db.add(risk)
    db.commit()
    db.refresh(risk)

    return risk


@router.patch(
    "/{risk_id}/status",
    response_model=RiskResponse,
)
def update_risk_status(
    risk_id: int,
    status_data: RiskStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "ADMIN",
            "SECURITY_ANALYST",
        )
    ),
):
    allowed_statuses = {
        "OPEN",
        "MITIGATED",
        "ACCEPTED",
        "CLOSED",
    }

    if status_data.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid risk status",
        )

    risk = (
        db.query(Risk)
        .filter(
            Risk.id == risk_id
        )
        .first()
    )

    if not risk:
        raise HTTPException(
            status_code=404,
            detail="Risk not found",
        )

    risk.status = status_data.status

    db.commit()
    db.refresh(risk)

    return risk
