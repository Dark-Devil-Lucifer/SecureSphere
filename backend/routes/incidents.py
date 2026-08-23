from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.models.incident import Incident, IncidentTimeline
from backend.models.incident_schema import (
    IncidentCreate,
    IncidentResponse,
    IncidentUpdate,
    TimelineCreate,
)
from backend.models.asset import Asset
from backend.models.user import User
from backend.utils.dependencies import (
    get_current_user,
    require_roles
)

router = APIRouter(
    prefix="/api/incidents",
    tags=["Incidents"]
)


@router.get("")
def get_incidents(
    search: str | None = Query(
        default=None
    ),
    severity: str | None = Query(
        default=None
    ),
    incident_status: str | None = Query(
        default=None,
        alias="status"
    ),
    asset_id: int | None = Query(
        default=None
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "ADMIN",
            "SECURITY_ANALYST"
        )
    ),
):

    query = db.query(Incident)

    # Search incident ID, title,
    # investigation notes and evidence.
    if search:

        search_value = (
            f"%{search.strip()}%"
        )

        query = query.filter(
            (
                Incident.incident_id.ilike(
                    search_value
                )
            )
            |
            (
                Incident.title.ilike(
                    search_value
                )
            )
            |
            (
                Incident.investigation_notes.ilike(
                    search_value
                )
            )
            |
            (
                Incident.evidence.ilike(
                    search_value
                )
            )
        )

    # Severity filter
    if severity:

        severity = severity.upper()

        allowed_severities = {
            "INFORMATIONAL",
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL",
        }

        if severity not in allowed_severities:

            raise HTTPException(
                status_code=400,
                detail="Invalid incident severity"
            )

        query = query.filter(
            Incident.severity == severity
        )

    # Status filter
    if incident_status:

        incident_status = (
            incident_status.upper()
        )

        allowed_statuses = {
            "OPEN",
            "INVESTIGATING",
            "CONTAINED",
            "RESOLVED",
            "CLOSED",
        }

        if incident_status not in allowed_statuses:

            raise HTTPException(
                status_code=400,
                detail="Invalid incident status"
            )

        query = query.filter(
            Incident.status ==
            incident_status
        )

    # Asset filter
    if asset_id is not None:

        query = query.filter(
            Incident.asset_id == asset_id
        )

    return (
        query
        .order_by(Incident.id.desc())
        .all()
    )

@router.get("/{incident_id}")
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    incident = (
        db.query(Incident)
        .filter(
            Incident.id == incident_id
        )
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    return incident

@router.post(
    "",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED
)

def create_incident(
    data: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    existing = (
        db.query(Incident)
        .filter(
            Incident.incident_id ==
            data.incident_id
        )
        .first()
    )

    if existing:

        raise HTTPException(
            status_code=409,
            detail="Incident ID already exists"
        )


    asset = (
        db.query(Asset)
        .filter(
            Asset.id == data.asset_id
        )
        .first()
    )

    if not asset:

        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )


    incident = Incident(
        incident_id=data.incident_id,
        alert_id=data.alert_id,
        asset_id=data.asset_id,
        title=data.title,
        severity=data.severity,
        detection_time=data.detection_time,
        assigned_analyst=data.assigned_analyst,
        status="OPEN",
        investigation_notes=data.investigation_notes,
        evidence=data.evidence,
        root_cause=data.root_cause,
        containment_action=data.containment_action,
        resolution=data.resolution,
        preventive_action=data.preventive_action,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


    db.add(incident)
    db.commit()
    db.refresh(incident)


    timeline = IncidentTimeline(
        incident_id=incident.id,
        event_time=datetime.utcnow(),
        action="INCIDENT_CREATED",
        description="Incident created in SecureSphere.",
        performed_by=current_user.id,
        created_at=datetime.utcnow(),
    )


    db.add(timeline)
    db.commit()


    return incident


@router.put("/{incident_id}")
def update_incident(
    incident_id: int,
    data: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
	require_roles(
            "ADMIN",
            "SECURITY_ANALYST"
    	)
    ),
):

    incident = (
        db.query(Incident)
        .filter(
            Incident.id == incident_id
        )
        .first()
    )

    if not incident:

        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )


    changes = data.model_dump(
        exclude_unset=True
    )


    old_status = incident.status


    for field, value in changes.items():

        setattr(
            incident,
            field,
            value
        )


    incident.updated_at = datetime.utcnow()


    db.commit()
    db.refresh(incident)


    if (
        "status" in changes
        and changes["status"] != old_status
    ):

        timeline = IncidentTimeline(
            incident_id=incident.id,
            event_time=datetime.utcnow(),
            action="STATUS_CHANGED",
            description=(
                f"Incident status changed "
                f"from {old_status} "
                f"to {incident.status}."
            ),
            performed_by=current_user.id,
            created_at=datetime.utcnow(),
        )

        db.add(timeline)
        db.commit()


    return incident


@router.get("/{incident_id}/timeline")
def get_incident_timeline(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    incident = (
        db.query(Incident)
        .filter(
            Incident.id == incident_id
        )
        .first()
    )

    if not incident:

        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )


    return (
        db.query(IncidentTimeline)
        .filter(
            IncidentTimeline.incident_id ==
            incident_id
        )
        .order_by(
            IncidentTimeline.event_time.asc()
        )
        .all()
    )


@router.post(
    "/{incident_id}/timeline",
    status_code=status.HTTP_201_CREATED
)
def add_timeline_entry(
    incident_id: int,
    data: TimelineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    incident = (
        db.query(Incident)
        .filter(
            Incident.id == incident_id
        )
        .first()
    )

    if not incident:

        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )


    timeline = IncidentTimeline(
        incident_id=incident.id,
        event_time=data.event_time,
        action=data.action,
        description=data.description,
        performed_by=current_user.id,
        created_at=datetime.utcnow(),
    )


    db.add(timeline)
    db.commit()
    db.refresh(timeline)


    return timeline
