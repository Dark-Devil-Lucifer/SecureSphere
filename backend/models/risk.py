from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.config.database import Base


class Risk(Base):
    __tablename__ = "risks"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    risk_id = Column(
        String(30),
        unique=True,
        nullable=False
    )

    asset_id = Column(
        Integer,
        ForeignKey(
            "assets.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    vulnerability_id = Column(
        Integer,
        ForeignKey(
            "vulnerabilities.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    threat = Column(
        String(255),
        nullable=False
    )

    vulnerability = Column(
        Text,
        nullable=True
    )

    likelihood = Column(
        Integer,
        nullable=False
    )

    impact = Column(
        Integer,
        nullable=False
    )

    risk_score = Column(
        Integer,
        nullable=False
    )

    risk_level = Column(
        Enum(
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL"
        ),
        nullable=False,
        index=True
    )

    mitigation = Column(
        Text,
        nullable=True
    )

    status = Column(
        Enum(
            "OPEN",
            "MITIGATED",
            "ACCEPTED",
            "CLOSED"
        ),
        nullable=False,
        default="OPEN",
        index=True
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

    asset = relationship(
        "Asset",
        foreign_keys=[asset_id]
    )

    vulnerability_record = relationship(
        "Vulnerability",
        foreign_keys=[vulnerability_id]
    )
