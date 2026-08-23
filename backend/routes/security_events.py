from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.models.security_event import SecurityEvent
from backend.models.security_event_schema import (
    SecurityEventCreate,
    SecurityEventStatusUpdate,
    SecurityEventResponse,
)
from backend.models.asset import Asset
from backend.services.correlation_engine import (
    correlate_failed_login_spike
)
from backend.services.detection_engine import (
    generate_alert_for_event
)
from backend.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/security-events",
    tags=["Security Events"]
)


ALLOWED_CATEGORIES = {
    "AUTHENTICATION",
    "SYSTEM",
    "APPLICATION",
    "NETWORK",
    "PERMISSION",
    "SECURITY_ALERT",
}


ALLOWED_SEVERITIES = {
    "INFORMATIONAL",
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
}


ALLOWED_STATUSES = {
    "NEW",
    "REVIEWED",
    "RESOLVED",
}


@router.get(
    "",
    response_model=list[SecurityEventResponse]
)
def get_security_events(

    search: str | None = Query(
        default=None
    ),

    category: str | None = Query(
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

    query = db.query(
        SecurityEvent
    )

    if search:

        search_value = (
            f"%{search}%"
        )

        query = query.filter(
            (
                SecurityEvent.event_id.ilike(
                    search_value
                )
            )
            |
            (
                SecurityEvent.event_type.ilike(
                    search_value
                )
            )
            |
            (
                SecurityEvent.description.ilike(
                    search_value
                )
            )
            |
            (
                SecurityEvent.source.ilike(
                    search_value
                )
            )
        )


    if category:

        category = category.upper()

        if category not in ALLOWED_CATEGORIES:

            raise HTTPException(
                status_code=400,
                detail="Invalid event category"
            )

        query = query.filter(
            SecurityEvent.category
            == category
        )


    if severity:

        severity = severity.upper()

        if severity not in ALLOWED_SEVERITIES:

            raise HTTPException(
                status_code=400,
                detail="Invalid severity"
            )

        query = query.filter(
            SecurityEvent.severity
            == severity
        )


    if status:

        status = status.upper()

        if status not in ALLOWED_STATUSES:

            raise HTTPException(
                status_code=400,
                detail="Invalid status"
            )

        query = query.filter(
            SecurityEvent.status
            == status
        )


    if asset_id:

        query = query.filter(
            SecurityEvent.asset_id
            == asset_id
        )


    return (
        query
        .order_by(
            SecurityEvent.event_timestamp.desc()
        )
        .all()
    )


@router.get(
    "/{event_id}",
    response_model=SecurityEventResponse
)
def get_security_event(

    event_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    ),

):

    event = db.query(
        SecurityEvent
    ).filter(
        SecurityEvent.id == event_id
    ).first()


    if not event:

        raise HTTPException(
            status_code=404,
            detail="Security event not found"
        )


    return event


@router.post(
    "",
    response_model=SecurityEventResponse,
    status_code=201
)
def create_security_event(

    event_data: SecurityEventCreate,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    ),

):

    if (
        event_data.category.upper()
        not in ALLOWED_CATEGORIES
    ):

        raise HTTPException(
            status_code=400,
            detail="Invalid event category"
        )


    if (
        event_data.severity.upper()
        not in ALLOWED_SEVERITIES
    ):

        raise HTTPException(
            status_code=400,
            detail="Invalid severity"
        )


    asset = db.query(
        Asset
    ).filter(
        Asset.id ==
        event_data.asset_id
    ).first()


    if not asset:

        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )


    existing = db.query(
        SecurityEvent
    ).filter(
        SecurityEvent.event_id ==
        event_data.event_id
    ).first()


    if existing:

        raise HTTPException(
            status_code=409,
            detail="Event ID already exists"
        )


    event = SecurityEvent(

        event_id=
            event_data.event_id,

        asset_id=
            event_data.asset_id,

        event_timestamp=
            event_data.event_timestamp,

        source=
            event_data.source,

        event_type=
            event_data.event_type,

        category=
            event_data.category.upper(),

        severity=
            event_data.severity.upper(),

        description=
            event_data.description,

        raw_data=
            event_data.raw_data,

        status="NEW",

        created_at=datetime.utcnow(),

    )

    try:
       db.add(event)

       db.flush()
       db.refresh(event)

       generate_alert_for_event(
           db,
           event
       )

       correlation_alert = correlate_failed_login_spike(
           db,
           event
       )

       if correlation_alert:
           generate_incident_for_alert(
               db,
               correlation_alert
           )

       db.commit()
       db.refresh(event)

       return event

    except Exception:
        db.rollback()
        raise


@router.patch(
    "/{event_id}/status",
    response_model=SecurityEventResponse
)
def update_security_event_status(

    event_id: int,

    status_data:
        SecurityEventStatusUpdate,

    db: Session = Depends(get_db),

    current_user=Depends(
        get_current_user
    ),

):

    new_status = (
        status_data.status
        .upper()
    )


    if new_status not in ALLOWED_STATUSES:

        raise HTTPException(
            status_code=400,
            detail="Invalid event status"
        )


    event = db.query(
        SecurityEvent
    ).filter(
        SecurityEvent.id ==
        event_id
    ).first()


    if not event:

        raise HTTPException(
            status_code=404,
            detail="Security event not found"
        )


    event.status = new_status

    db.commit()

    db.refresh(event)

    return event
