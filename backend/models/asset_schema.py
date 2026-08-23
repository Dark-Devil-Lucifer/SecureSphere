from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AssetCreate(BaseModel):

    asset_name: str = Field(
        min_length=1,
        max_length=150
    )

    asset_type: str = Field(
        min_length=1,
        max_length=50
    )

    operating_system: Optional[str] = Field(
        default=None,
        max_length=100
    )

    ip_address: Optional[str] = Field(
        default=None,
        max_length=45
    )

    hostname: Optional[str] = Field(
        default=None,
        max_length=150
    )

    owner: Optional[str] = Field(
        default=None,
        max_length=150
    )

    criticality: str = "MEDIUM"

    environment: str = "TEST"


class AssetUpdate(BaseModel):

    asset_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=150
    )

    asset_type: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    operating_system: Optional[str] = Field(
        default=None,
        max_length=100
    )

    ip_address: Optional[str] = Field(
        default=None,
        max_length=45
    )

    hostname: Optional[str] = Field(
        default=None,
        max_length=150
    )

    owner: Optional[str] = Field(
        default=None,
        max_length=150
    )

    criticality: Optional[str] = None

    environment: Optional[str] = None


class AssetStatusUpdate(BaseModel):

    status: str


class AssetResponse(BaseModel):

    id: int
    asset_name: str
    asset_type: str
    operating_system: Optional[str]
    ip_address: Optional[str]
    hostname: Optional[str]
    owner: Optional[str]
    criticality: str
    environment: str
    status: str
    last_assessment_date: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True
    )
