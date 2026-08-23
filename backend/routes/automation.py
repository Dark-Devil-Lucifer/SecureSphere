from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from sqlalchemy.orm import Session
from backend.config.database import get_db
from backend.models.automation import AutomationLog
from backend.services.health_checker import (
    run_security_health_check
)
from backend.services.failed_login_analyzer import (
    run_failed_login_analyzer,
)
from backend.services.automation_logger import (
    record_automation_execution
)
from backend.utils.dependencies import get_current_user
from backend.services.system_monitor import (
    run_system_monitor,
)

router = APIRouter(
    prefix="/api/automation",
    tags=["Automation"]
)


@router.post("/health/check")
def run_health_check(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        result = run_security_health_check(db)

        record_automation_execution(
            db=db,
            automation_name=result["automation_name"],
            status="SUCCESS",
            output_summary=result["summary"],
            output_data=result,
            input_source="SecureSphere database",
        )

        db.commit()

        return result

    except Exception as exc:
        db.rollback()

        try:
            record_automation_execution(
                db=db,
                automation_name="SECURITY_HEALTH_CHECK",
                status="FAILED",
                output_summary="Security health check failed.",
                input_source="SecureSphere database",
                error_message=str(exc),
            )

            db.commit()

        except Exception:
            db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Security health check failed"
        )


@router.get("/health")
def get_latest_health_check(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    log = (
        db.query(AutomationLog)
        .filter(
            AutomationLog.automation_name ==
            "SECURITY_HEALTH_CHECK",
            AutomationLog.status == "SUCCESS",
        )
        .order_by(
            AutomationLog.id.desc()
        )
        .first()
    )

    if not log:
        raise HTTPException(
            status_code=404,
            detail="No successful health check found"
        )

    import json

    return {
        "id": log.id,
        "automation_name": log.automation_name,
        "execution_time": log.execution_time,
        "status": log.status,
        "output_summary": log.output_summary,
        "output_data": (
            json.loads(log.output_data)
            if log.output_data
            else None
        ),
    }


@router.get("/logs")
def get_automation_logs(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    logs = (
        db.query(AutomationLog)
        .order_by(
            AutomationLog.id.desc()
        )
        .limit(50)
        .all()
    )

    return [
        {
            "id": log.id,
            "automation_name": log.automation_name,
            "execution_time": log.execution_time,
            "status": log.status,
            "input_source": log.input_source,
            "output_summary": log.output_summary,
            "error_message": log.error_message,
        }
        for log in logs
    ]

@router.get("/system-monitor")
def get_system_monitor(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    import json

    result = run_system_monitor()

    log = record_automation_execution(
        db=db,
        automation_name=result["automation_name"],
        status="SUCCESS",
        output_summary=result["summary"],
        output_data=result,
        input_source="Local system",
    )

    db.commit()

    return {
        "id": log.id,
        "automation_name": log.automation_name,
        "execution_time": log.execution_time,
        "status": log.status,
        "output_summary": log.output_summary,
        "output_data": (
            json.loads(log.output_data)
            if log.output_data
            else None
        ),
    }

@router.post("/integrity/check")
def run_integrity_check(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        from backend.services.integrity_checker import check_integrity

        result = check_integrity(db)

        return result

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Integrity check failed"
        )


@router.get("/integrity")
def get_latest_integrity_check(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    import json

    log = (
        db.query(AutomationLog)
        .filter(
            AutomationLog.automation_name == "INTEGRITY_CHECK",
            AutomationLog.status == "SUCCESS",
        )
        .order_by(
            AutomationLog.id.desc()
        )
        .first()
    )

    if not log:
        raise HTTPException(
            status_code=404,
            detail="No integrity check found"
        )

    return {
        "id": log.id,
        "automation_name": log.automation_name,
        "execution_time": log.execution_time,
        "status": log.status,
        "output_summary": log.output_summary,
        "output_data": (
            json.loads(log.output_data)
            if log.output_data
            else None
        ),
    }
@router.post("/failed-logins")
def run_failed_login_analysis(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Analyze failed-login activity from SecureSphere
    security events and persist the execution result.
    """

    try:
        result = run_failed_login_analyzer(db)

        record_automation_execution(
            db=db,
            automation_name=result["automation_name"],
            status="SUCCESS",
            output_summary=result["summary"],
            output_data=result,
            input_source="SecureSphere security_events database",
        )

        db.commit()

        return result

    except Exception as exc:
        db.rollback()

        try:
            record_automation_execution(
                db=db,
                automation_name="FAILED_LOGIN_ANALYZER",
                status="FAILED",
                output_summary="Failed Login Analyzer execution failed.",
                input_source="SecureSphere security_events database",
                error_message=str(exc),
            )

            db.commit()

        except Exception:
            db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed Login Analyzer execution failed",
        )
@router.get("/failed-logins")
def get_latest_failed_login_analysis(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    import json

    log = (
        db.query(AutomationLog)
        .filter(
            AutomationLog.automation_name ==
            "FAILED_LOGIN_ANALYZER",
            AutomationLog.status == "SUCCESS",
        )
        .order_by(
            AutomationLog.id.desc()
        )
        .first()
    )

    if not log:
        raise HTTPException(
            status_code=404,
            detail="No successful failed-login analysis found",
        )

    return {
        "id": log.id,
        "automation_name": log.automation_name,
        "execution_time": log.execution_time,
        "status": log.status,
        "output_summary": log.output_summary,
        "output_data": (
            json.loads(log.output_data)
            if log.output_data
            else None
        ),
    }
