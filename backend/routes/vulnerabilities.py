from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.models.asset import Asset
from backend.models.assessment import Assessment
from backend.models.user import User
from backend.models.vulnerability import Vulnerability
from backend.models.vulnerability_schema import (
    VulnerabilityCreate,
    VulnerabilityResponse,
    VulnerabilityStatusUpdate,
    VulnerabilityUpdate
)
from backend.utils.dependencies import (
    get_current_user,
    require_roles
)
from backend.utils.vulnerability_validation import (
    validate_risk_level,
    validate_vulnerability_severity,
    validate_vulnerability_status
)
from backend.services.vulnerability_alert_engine import (
    generate_alert_for_vulnerability,
)


router = APIRouter(
    prefix="/api/vulnerabilities",
    tags=["Vulnerabilities"]
)


@router.post(
    "",
    response_model=VulnerabilityResponse,
    status_code=status.HTTP_201_CREATED
)
def create_vulnerability(

    vulnerability_data: VulnerabilityCreate,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles(
            "ADMIN",
            "SECURITY_ANALYST"
        )
    )
):

    # -----------------------------------------
    # Verify asset
    # -----------------------------------------

    asset = (
        db.query(Asset)
        .filter(
            Asset.id ==
            vulnerability_data.asset_id
        )
        .first()
    )

    if not asset:

        raise HTTPException(
            status_code=404,
            detail="Associated asset not found"
        )


    # -----------------------------------------
    # Verify assessment if supplied
    # -----------------------------------------

    if vulnerability_data.assessment_id:

        assessment = (
            db.query(Assessment)
            .filter(
                Assessment.id ==
                vulnerability_data.assessment_id
            )
            .first()
        )

        if not assessment:

            raise HTTPException(
                status_code=404,
                detail="Assessment not found"
            )

        if assessment.asset_id != vulnerability_data.asset_id:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Assessment does not belong "
                    "to the selected asset"
                )
            )


    # -----------------------------------------
    # Check duplicate vulnerability ID
    # -----------------------------------------

    existing = (
        db.query(Vulnerability)
        .filter(
            Vulnerability.vulnerability_id
            ==
            vulnerability_data.vulnerability_id
        )
        .first()
    )

    if existing:

        raise HTTPException(
            status_code=409,
            detail="Vulnerability ID already exists"
        )


    # -----------------------------------------
    # Validate severity
    # -----------------------------------------

    try:

        severity = (
            validate_vulnerability_severity(
                vulnerability_data.severity
            )
        )

        risk_level = (
            validate_risk_level(
                vulnerability_data.risk_level
            )
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


    # -----------------------------------------
    # Create record
    # -----------------------------------------

    vulnerability = Vulnerability(

        vulnerability_id=(
            vulnerability_data.vulnerability_id
        ),

        assessment_id=(
            vulnerability_data.assessment_id
        ),

        asset_id=(
            vulnerability_data.asset_id
        ),

        title=(
            vulnerability_data.title
        ),

        category=(
            vulnerability_data.category
        ),

        description=(
            vulnerability_data.description
        ),

        severity=severity,

        risk_level=risk_level,

        date_identified=(
            vulnerability_data.date_identified
        ),

        identified_by=current_user.id,

        evidence=(
            vulnerability_data.evidence
        ),

        remediation=(
            vulnerability_data.remediation
        ),

        status="OPEN"
    )


    db.add(vulnerability)

    db.flush()
    db.refresh(vulnerability)

    generate_alert_for_vulnerability(
	db,
        vulnerability,
    )

    db.commit()

    db.refresh(vulnerability)

    return vulnerability


@router.get(
    "",
    response_model=list[VulnerabilityResponse]
)
def list_vulnerabilities(

    search: Optional[str] = Query(
        default=None
    ),

    severity: Optional[str] = Query(
        default=None
    ),

    vulnerability_status: Optional[str] = Query(
        default=None,
        alias="status"
    ),

    asset_id: Optional[int] = Query(
        default=None
    ),

    category: Optional[str] = Query(
        default=None
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    query = db.query(
        Vulnerability
    )


    if search:

        search_value = f"%{search}%"

        query = query.filter(
            (
                Vulnerability.vulnerability_id
                .ilike(search_value)
            )
            |
            (
                Vulnerability.title
                .ilike(search_value)
            )
            |
            (
                Vulnerability.description
                .ilike(search_value)
            )
            |
            (
                Vulnerability.category
                .ilike(search_value)
            )
        )


    if severity:

        try:

            severity = (
                validate_vulnerability_severity(
                    severity
                )
            )

        except ValueError as error:

            raise HTTPException(
                status_code=400,
                detail=str(error)
            )

        query = query.filter(
            Vulnerability.severity ==
            severity
        )


    if vulnerability_status:

        try:

            vulnerability_status = (
                validate_vulnerability_status(
                    vulnerability_status
                )
            )

        except ValueError as error:

            raise HTTPException(
                status_code=400,
                detail=str(error)
            )

        query = query.filter(
            Vulnerability.status ==
            vulnerability_status
        )


    if asset_id:

        query = query.filter(
            Vulnerability.asset_id ==
            asset_id
        )


    if category:

        query = query.filter(
            Vulnerability.category
            .ilike(category)
        )


    return (
        query
        .order_by(
            Vulnerability.id.desc()
        )
        .all()
    )


@router.get(
    "/{vulnerability_id}",
    response_model=VulnerabilityResponse
)
def get_vulnerability(

    vulnerability_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    vulnerability = (
        db.query(Vulnerability)
        .filter(
            Vulnerability.id ==
            vulnerability_id
        )
        .first()
    )

    if not vulnerability:

        raise HTTPException(
            status_code=404,
            detail="Vulnerability not found"
        )

    return vulnerability


@router.put(
    "/{vulnerability_id}",
    response_model=VulnerabilityResponse
)
def update_vulnerability(

    vulnerability_id: int,

    vulnerability_data: VulnerabilityUpdate,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles(
            "ADMIN",
            "SECURITY_ANALYST"
        )
    )
):

    vulnerability = (
        db.query(Vulnerability)
        .filter(
            Vulnerability.id ==
            vulnerability_id
        )
        .first()
    )

    if not vulnerability:

        raise HTTPException(
            status_code=404,
            detail="Vulnerability not found"
        )


    update_data = (
        vulnerability_data
        .model_dump(
            exclude_unset=True
        )
    )


    if "asset_id" in update_data:

        asset = (
            db.query(Asset)
            .filter(
                Asset.id ==
                update_data["asset_id"]
            )
            .first()
        )

        if not asset:

            raise HTTPException(
                status_code=404,
                detail="Asset not found"
            )

    if "assessment_id" in update_data:

        if update_data["assessment_id"]:

            assessment = (
                db.query(Assessment)
                .filter(
                    Assessment.id ==
                    update_data["assessment_id"]
                )
                .first()
            )

            if not assessment:

                raise HTTPException(
                    status_code=404,
                    detail="Assessment not found"
                )

            effective_asset_id = update_data.get(
                "asset_id",
                vulnerability.asset_id
            )

            if assessment.asset_id != effective_asset_id:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Assessment does not belong "
                        "to the selected asset"
                    )
                )
                

    if "severity" in update_data:

        try:

            update_data["severity"] = (
                validate_vulnerability_severity(
                    update_data["severity"]
                )
            )

        except ValueError as error:

            raise HTTPException(
                status_code=400,
                detail=str(error)
            )


    if "risk_level" in update_data:

        try:

            update_data["risk_level"] = (
                validate_risk_level(
                    update_data["risk_level"]
                )
            )

        except ValueError as error:

            raise HTTPException(
                status_code=400,
                detail=str(error)
            )


    for field, value in update_data.items():

        setattr(
            vulnerability,
            field,
            value
        )


    db.commit()

    db.refresh(vulnerability)

    return vulnerability


@router.patch(
    "/{vulnerability_id}/status",
    response_model=VulnerabilityResponse
)
def update_vulnerability_status(

    vulnerability_id: int,

    status_data: VulnerabilityStatusUpdate,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles(
            "ADMIN",
            "SECURITY_ANALYST"
        )
    )
):

    vulnerability = (
        db.query(Vulnerability)
        .filter(
            Vulnerability.id ==
            vulnerability_id
        )
        .first()
    )

    if not vulnerability:

        raise HTTPException(
            status_code=404,
            detail="Vulnerability not found"
        )


    try:

        new_status = (
            validate_vulnerability_status(
                status_data.status
            )
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


    vulnerability.status = new_status

    db.commit()

    db.refresh(vulnerability)

    return vulnerability


@router.delete(
    "/{vulnerability_id}"
)
def archive_vulnerability(

    vulnerability_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles("ADMIN")
    )
):

    vulnerability = (
        db.query(Vulnerability)
        .filter(
            Vulnerability.id ==
            vulnerability_id
        )
        .first()
    )

    if not vulnerability:

        raise HTTPException(
            status_code=404,
            detail="Vulnerability not found"
        )


    vulnerability.status = "CLOSED"

    db.commit()


    return {
        "message":
            "Vulnerability closed successfully",

        "vulnerability_id":
            vulnerability.id,

        "status":
            vulnerability.status
    }
