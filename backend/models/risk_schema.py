from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RiskCreate(BaseModel):
    risk_id: str = Field(..., max_length=30)
    asset_id: int
    vulnerability_id: Optional[int] = None

    threat: str = Field(..., max_length=255)
    vulnerability: Optional[str] = None

    likelihood: int = Field(..., ge=1, le=5)
    impact: int = Field(..., ge=1, le=5)

    mitigation: Optional[str] = None


class RiskStatusUpdate(BaseModel):
    status: str


class RiskResponse(BaseModel):
    id: int
    risk_id: str
    asset_id: int
    vulnerability_id: Optional[int]

    threat: str
    vulnerability: Optional[str]

    likelihood: int
    impact: int
    risk_score: int
    risk_level: str

    mitigation: Optional[str]
    status: str

    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
