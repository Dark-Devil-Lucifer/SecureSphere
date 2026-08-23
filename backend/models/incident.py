from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Enum,
)
from sqlalchemy.orm import relationship

from backend.config.database import Base


class Incident(Base):

    __tablename__ = "incidents"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    incident_id = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    alert_id = Column(
        Integer,
        ForeignKey(
            "alerts.id",
            ondelete="SET NULL",
        ),
        unique=True,
        nullable=True,
    )

    asset_id = Column(
        Integer,
        ForeignKey(
            "assets.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    severity = Column(
        Enum(
            "INFORMATIONAL",
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL",
        ),
        nullable=False,
        index=True,
    )

    detection_time = Column(
        DateTime,
        nullable=False,
    )

    assigned_analyst = Column(
        Integer,
        ForeignKey(
            "users.id",
        ),
        nullable=True,
    )

    status = Column(
        Enum(
            "OPEN",
            "INVESTIGATING",
            "CONTAINED",
            "RESOLVED",
            "CLOSED",
        ),
        nullable=False,
        default="OPEN",
        index=True,
    )

    investigation_notes = Column(
        Text,
        nullable=True,
    )

    evidence = Column(
        Text,
        nullable=True,
    )

    root_cause = Column(
        Text,
        nullable=True,
    )

    containment_action = Column(
        Text,
        nullable=True,
    )

    resolution = Column(
        Text,
        nullable=True,
    )

    preventive_action = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class IncidentTimeline(Base):

    __tablename__ = "incident_timeline"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    incident_id = Column(
        Integer,
        ForeignKey(
            "incidents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    event_time = Column(
        DateTime,
        nullable=False,
    )

    action = Column(
        String(150),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    performed_by = Column(
        Integer,
        ForeignKey(
            "users.id",
        ),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )
