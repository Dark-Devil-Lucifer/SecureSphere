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


class SecurityEvent(Base):

    __tablename__ = "security_events"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    event_id = Column(
        String(30),
        unique=True,
        nullable=False,
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

    event_timestamp = Column(
        DateTime,
        nullable=False,
        index=True
    )

    source = Column(
        String(150),
        nullable=True
    )

    event_type = Column(
        String(100),
        nullable=False
    )

    category = Column(
        Enum(
            "AUTHENTICATION",
            "SYSTEM",
            "APPLICATION",
            "NETWORK",
            "PERMISSION",
            "SECURITY_ALERT"
        ),
        nullable=False,
        index=True
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

    description = Column(
        Text,
        nullable=True
    )

    status = Column(
        Enum(
            "NEW",
            "REVIEWED",
            "RESOLVED"
        ),
        nullable=False,
        default="NEW"
    )

    raw_data = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        nullable=True
    )

    asset = relationship(
        "Asset"
    )
