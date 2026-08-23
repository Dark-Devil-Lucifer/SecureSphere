from sqlalchemy import Column, DateTime, Enum, Integer, String
from sqlalchemy.sql import func

from backend.config.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    asset_name = Column(
        String(150),
        nullable=False
    )

    asset_type = Column(
        String(50),
        nullable=False
    )

    operating_system = Column(
        String(100),
        nullable=True
    )

    ip_address = Column(
        String(45),
        nullable=True
    )

    hostname = Column(
        String(150),
        nullable=True
    )

    owner = Column(
        String(150),
        nullable=True
    )

    criticality = Column(
        Enum(
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL"
        ),
        nullable=False,
        default="MEDIUM"
    )

    environment = Column(
        Enum(
            "DEVELOPMENT",
            "TEST",
            "PRODUCTION_SIMULATION"
        ),
        nullable=False,
        default="TEST"
    )

    status = Column(
        Enum(
            "ACTIVE",
            "INACTIVE",
            "RETIRED"
        ),
        nullable=False,
        default="ACTIVE"
    )

    last_assessment_date = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )
