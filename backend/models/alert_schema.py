from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AlertStatusUpdate(BaseModel):

    status: str


class AlertResponse(BaseModel):

    id: int

    alert_id: str

    event_id: Optional[int]

    asset_id: int

    rule_name: str

    title: str

    severity: str

    trigger_time: datetime

    description: Optional[str]

    status: str

    created_at: Optional[datetime]

    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
