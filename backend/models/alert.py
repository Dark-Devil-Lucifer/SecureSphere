from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Enum,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from backend.config.database import Base


class Alert(Base):

    __tablename__ = "alerts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    alert_id = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True
    )

    event_id = Column(
        Integer,
        ForeignKey(
            "security_events.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
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

    rule_name = Column(
        String(150),
        nullable=False
    )

    title = Column(
        String(255),
        nullable=False
    )

    severity = Column(
        Enum(
            "INFORMATIONAL",
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL"
        ),
        nullable=False,
        index=True
    )

    trigger_time = Column(
        DateTime,
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    status = Column(
        Enum(
            "NEW",
            "INVESTIGATING",
            "RESOLVED",
            "CLOSED"
        ),
        nullable=False,
        default="NEW",
        index=True
    )

    created_at = Column(
        DateTime,
        nullable=True
    )

    updated_at = Column(
        DateTime,
        nullable=True
    )

    event = relationship(
        "SecurityEvent"
    )

    asset = relationship(
        "Asset"
    )
