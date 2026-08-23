from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.models.report import Report
from backend.models.user import User
from backend.services.report_generator import (
    build_security_posture_report,
)
from backend.services.extended_report_generator import (
    build_vulnerability_assessment_report,
    build_security_incident_report,
    build_risk_assessment_report,
    build_asset_security_report,
)
from backend.utils.dependencies import (
    get_current_user,
    require_roles,
)


router = APIRouter(
    prefix="/api/reports",
    tags=["Reports"],
)


@router.post(
    "/security-posture",
    status_code=status.HTTP_201_CREATED,
)
def generate_security_posture_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "ADMIN",
            "SECURITY_ANALYST",
        )
    ),
):
    """
    Generate and persist a Security Posture Report.
    """

    try:

        result = build_security_posture_report(
            db=db,
            generated_by=current_user.id,
        )

        return result

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Report generation failed: "
                f"{str(error)}"
            ),
        )

@router.post(
    "/vulnerability-assessment",
    status_code=status.HTTP_201_CREATED,
)
def generate_vulnerability_assessment_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "ADMIN",
            "SECURITY_ANALYST",
        )
    ),
):
    try:
        return build_vulnerability_assessment_report(
            db=db,
            generated_by=current_user.id,
        )
    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {str(error)}",
        )


@router.post(
    "/security-incident",
    status_code=status.HTTP_201_CREATED,
)
def generate_security_incident_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "ADMIN",
            "SECURITY_ANALYST",
        )
    ),
):
    try:
        return build_security_incident_report(
            db=db,
            generated_by=current_user.id,
        )
    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {str(error)}",
        )


@router.post(
    "/risk-assessment",
    status_code=status.HTTP_201_CREATED,
)
def generate_risk_assessment_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "ADMIN",
            "SECURITY_ANALYST",
        )
    ),
):
    try:
        return build_risk_assessment_report(
            db=db,
            generated_by=current_user.id,
        )
    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {str(error)}",
        )


@router.post(
    "/asset-security",
    status_code=status.HTTP_201_CREATED,
)
def generate_asset_security_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "ADMIN",
            "SECURITY_ANALYST",
        )
    ),
):
    try:
        return build_asset_security_report(
            db=db,
            generated_by=current_user.id,
        )
    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {str(error)}",
        )

@router.get("")
def get_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Return report history.
    """

    return (
        db.query(Report)
        .order_by(
            Report.id.desc()
        )
        .all()
    )


@router.get("/{report_id}")
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Return a specific report record.
    """

    report = (
        db.query(Report)
        .filter(
            Report.id == report_id
        )
        .first()
    )

    if not report:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    return report


@router.get("/{report_id}/download")
def download_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Download a generated report PDF.
    """

    report = (
        db.query(Report)
        .filter(
            Report.id == report_id
        )
        .first()
    )

    if not report:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    if report.status != "GENERATED":

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Report is not available "
                "for download"
            ),
        )

    if not report.file_path:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file path is missing",
        )

    file_path = Path(
        report.file_path
    )

    if not file_path.is_file():

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found",
        )

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=report.file_name,
    )
