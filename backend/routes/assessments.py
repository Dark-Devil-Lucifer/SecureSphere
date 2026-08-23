from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.models.assessment import Assessment
from backend.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/assessments",
    tags=["Assessments"]
)


@router.get("")
def get_assessments(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return (
        db.query(Assessment)
        .order_by(Assessment.id.desc())
        .all()
    )


@router.get("/{assessment_id}")
def get_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    assessment = (
        db.query(Assessment)
        .filter(
            Assessment.id == assessment_id
        )
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="Assessment not found"
        )

    return assessment


@router.post(
    "",
    status_code=201
)
def create_assessment(
    assessment_data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    required_fields = [
        "asset_id",
        "assessment_type",
        "performed_by",
        "assessment_date"
    ]

    for field in required_fields:

        if field not in assessment_data:

            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}"
            )


    try:

        assessment_date = datetime.fromisoformat(
            assessment_data["assessment_date"]
        )

    except (
        ValueError,
        TypeError
    ):

        raise HTTPException(
            status_code=400,
            detail="Invalid assessment_date format"
        )


    allowed_statuses = {
        "PLANNED",
        "IN_PROGRESS",
        "COMPLETED",
        "CANCELLED"
    }


    requested_status = assessment_data.get(
        "status",
        "PLANNED"
    )


    if requested_status not in allowed_statuses:

        raise HTTPException(
            status_code=400,
            detail="Invalid assessment status"
        )


    assessment = Assessment(
        asset_id=assessment_data["asset_id"],
        assessment_type=assessment_data["assessment_type"],
        performed_by=assessment_data["performed_by"],
        assessment_date=assessment_date,
        status=requested_status,
        summary=assessment_data.get(
            "summary"
        )
    )


    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return assessment


@router.patch(
    "/{assessment_id}/status"
)
def update_assessment_status(
    assessment_id: int,
    status_data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    allowed_statuses = {
        "PLANNED",
        "IN_PROGRESS",
        "COMPLETED",
        "CANCELLED"
    }


    status = status_data.get(
        "status"
    )


    if status not in allowed_statuses:

        raise HTTPException(
            status_code=400,
            detail="Invalid assessment status"
        )


    assessment = (
        db.query(Assessment)
        .filter(
            Assessment.id == assessment_id
        )
        .first()
    )


    if not assessment:

        raise HTTPException(
            status_code=404,
            detail="Assessment not found"
        )


    assessment.status = status

    db.commit()
    db.refresh(assessment)

    return assessment
