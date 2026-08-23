import json
from datetime import datetime

from sqlalchemy.orm import Session

from backend.models.automation import AutomationLog


def record_automation_execution(
    db: Session,
    automation_name: str,
    status: str,
    output_summary: str,
    output_data: dict | None = None,
    input_source: str | None = None,
    error_message: str | None = None,
):
    """
    Persist an automation execution in automation_logs.
    """

    log = AutomationLog(
        automation_name=automation_name,
        execution_time=datetime.utcnow(),
        status=status,
        input_source=input_source,
        output_summary=output_summary,
        output_data=(
            json.dumps(output_data)
            if output_data is not None
            else None
        ),
        error_message=error_message,
        created_at=datetime.utcnow(),
    )

    db.add(log)
    db.flush()

    return log
