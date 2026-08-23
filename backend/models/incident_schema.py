from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class IncidentCreate(BaseModel):

    incident_id: str = Field(
        min_length=1,
        max_length=30
    )

    alert_id: Optional[int] = None

    asset_id: int

    title: str = Field(
        min_length=1,
        max_length=255
    )

    severity: str

    detection_time: datetime

    assigned_analyst: Optional[int] = None

    investigation_notes: Optional[str] = None

    evidence: Optional[str] = None

    root_cause: Optional[str] = None

    containment_action: Optional[str] = None

    resolution: Optional[str] = None

    preventive_action: Optional[str] = None


class IncidentUpdate(BaseModel):

    title: Optional[str] = Field(
        default=None,
        max_length=255
    )

    severity: Optional[str] = None

    assigned_analyst: Optional[int] = None

    status: Optional[str] = None

    investigation_notes: Optional[str] = None

    evidence: Optional[str] = None

    root_cause: Optional[str] = None

    containment_action: Optional[str] = None

    resolution: Optional[str] = None

    preventive_action: Optional[str] = None


class IncidentResponse(BaseModel):

    id: int

    incident_id: str

    alert_id: Optional[int]

    asset_id: int

    title: str

    severity: str

    detection_time: datetime

    assigned_analyst: Optional[int]

    status: str

    investigation_notes: Optional[str]

    evidence: Optional[str]

    root_cause: Optional[str]

    containment_action: Optional[str]

    resolution: Optional[str]

    preventive_action: Optional[str]

    created_at: Optional[datetime]

    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class TimelineCreate(BaseModel):

    event_time: datetime

    action: str = Field(
        min_length=1,
        max_length=150
    )

    description: Optional[str] = None


class TimelineResponse(BaseModel):

    id: int

    incident_id: int

    event_time: datetime

    action: str

    description: Optional[str]

    performed_by: Optional[int]

    created_at: Optional[datetime]

    class Config:
        from_attributes = True
