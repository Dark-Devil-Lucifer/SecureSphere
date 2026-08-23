from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from backend.config.database import get_db
from backend.models.alert import Alert
from backend.models.alert_schema import (
    AlertResponse,
    AlertStatusUpdate,
)
from backend.models.incident import (
    Incident,
    IncidentTimeline,
)
from backend.models.user import User
from datetime import datetime
from backend.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/alerts",
    tags=["Alerts"]
)


ALLOWED_STATUSES = {
    "NEW",
    "INVESTIGATING",
    "RESOLVED",
    "CLOSED",
}


@router.get(
    "",
    response_model=list[AlertResponse]
)
def get_alerts(

    search: str | None = Query(
        default=None
    ),

    severity: str | None = Query(
        default=None
    ),

    status: str | None = Query(
        default=None
    ),

    asset_id: int | None = Query(
   	 default=None
    ),

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    ),

):

    query = db.query(Alert)


    if search:

        search_value = (
            f"%{search}%"
        )

        query = query.filter(
            (
                Alert.alert_id.ilike(
                    search_value
                )
            )
            |
            (
                Alert.rule_name.ilike(
                    search_value
                )
            )
            |
            (
                Alert.title.ilike(
                    search_value
                )
            )
            |
            (
                Alert.description.ilike(
                    search_value
                )
            )
        )


    if severity:

        severity = severity.upper()

        query = query.filter(
            Alert.severity == severity
        )


    if status:

        status = status.upper()

        if status not in ALLOWED_STATUSES:

            raise HTTPException(
                status_code=400,
                detail="Invalid alert status"
            )

        query = query.filter(
            Alert.status == status
        )

    if asset_id is not None:

        query = query.filter(
            Alert.asset_id == asset_id
        )

    return (
        query
        .order_by(
            Alert.trigger_time.desc()
        )
        .all()
    )


@router.get(
    "/{alert_id}",
    response_model=AlertResponse
)
def get_alert(

    alert_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    ),

):

    alert = db.query(
        Alert
    ).filter(
        Alert.id == alert_id
    ).first()


    if not alert:

        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )


    return alert


@router.patch(
    "/{alert_id}/status",
    response_model=AlertResponse
)

@router.post(
    "/{alert_id}/convert-to-incident"
)
def convert_alert_to_incident(

    alert_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    ),

):

    # ---------------------------------------------
    # Find alert
    # ---------------------------------------------

    alert = (
        db.query(Alert)
        .filter(
            Alert.id == alert_id
        )
        .first()
    )

    if not alert:

        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    # ---------------------------------------------
    # Prevent duplicate incident
    # ---------------------------------------------

    existing = (
        db.query(Incident)
        .filter(
            Incident.alert_id == alert.id
        )
        .first()
    )

    if existing:

        return existing

    # ---------------------------------------------
    # Find active security analyst
    # ---------------------------------------------

    analyst = (
        db.query(User)
        .filter(
            User.role == "SECURITY_ANALYST",
            User.is_active == True
        )
        .order_by(User.id)
        .first()
    )

    assigned_analyst = (
        analyst.id
        if analyst
        else current_user.id
    )

    # ---------------------------------------------
    # Generate incident ID
    # ---------------------------------------------

    incident_id = (
        f"INC-{datetime.utcnow().strftime('%Y')}-"
        f"{alert.id:03d}"
    )

    existing_id = (
        db.query(Incident)
        .filter(
            Incident.incident_id ==
            incident_id
        )
        .first()
    )

    if existing_id:

        incident_id = (
            f"INC-{datetime.utcnow().strftime('%Y')}-"
            f"{alert.id:03d}-1"
        )

    # ---------------------------------------------
    # Create incident
    # ---------------------------------------------

    incident = Incident(

        incident_id=incident_id,

        alert_id=alert.id,

        asset_id=alert.asset_id,

        title=(
            f"Investigation: {alert.title}"
        ),

        severity=alert.severity,

        detection_time=alert.trigger_time,

        assigned_analyst=assigned_analyst,

        status="OPEN",

        investigation_notes=(
            "Incident manually created from "
            f"alert {alert.alert_id}."
        ),

        evidence=(
            alert.description
            or "Alert generated by the detection engine."
        ),

        root_cause=None,

        containment_action=None,

        resolution=None,

        preventive_action=(
            "Investigate the alert, determine root cause "
            "and review applicable security controls."
        ),

        created_at=datetime.utcnow(),

        updated_at=datetime.utcnow(),

    )

    db.add(incident)
    db.flush()

    # ---------------------------------------------
    # Create incident timeline entry
    # ---------------------------------------------

    timeline = IncidentTimeline(

        incident_id=incident.id,

        event_time=datetime.utcnow(),

        action="INCIDENT_CREATED_FROM_ALERT",

        description=(
            f"Incident manually created from "
            f"alert {alert.alert_id}."
        ),

        performed_by=current_user.id,

        created_at=datetime.utcnow(),

    )

    db.add(timeline)

    # ---------------------------------------------
    # Update alert
    # ---------------------------------------------

    if alert.status == "NEW":
        alert.status = "INVESTIGATING"

    alert.updated_at = datetime.utcnow()

    db.commit()

    db.refresh(incident)

    return incident

def update_alert_status(

    alert_id: int,

    status_data:
        AlertStatusUpdate,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    ),

):

    new_status = (
        status_data.status.upper()
    )


    if new_status not in ALLOWED_STATUSES:

        raise HTTPException(
            status_code=400,
            detail="Invalid alert status"
        )


    alert = db.query(
        Alert
    ).filter(
        Alert.id == alert_id
    ).first()


    if not alert:

        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )


    alert.status = new_status

    db.commit()

    db.refresh(alert)

    return alert
