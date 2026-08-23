from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SecurityEventCreate(BaseModel):

    event_id: str

    asset_id: int

    event_timestamp: datetime

    source: Optional[str] = None

    event_type: str

    category: str

    severity: str

    description: Optional[str] = None

    raw_data: Optional[str] = None


class SecurityEventStatusUpdate(BaseModel):

    status: str


class SecurityEventResponse(BaseModel):

    id: int

    event_id: str

    asset_id: int

    event_timestamp: datetime

    source: Optional[str]

    event_type: str

    category: str

    severity: str

    description: Optional[str]

    status: str

    raw_data: Optional[str]

    class Config:
        from_attributes = True
