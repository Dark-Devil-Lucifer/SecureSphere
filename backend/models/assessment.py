from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.config.database import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(
        Integer,
        primary_key=True,
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

    assessment_type = Column(
        String(100),
        nullable=False
    )

    performed_by = Column(
        Integer,
        ForeignKey(
            "users.id"
        ),
        nullable=False
    )

    assessment_date = Column(
        DateTime,
        nullable=False
    )

    status = Column(
        Enum(
            "PLANNED",
            "IN_PROGRESS",
            "COMPLETED",
            "CANCELLED"
        ),
        nullable=False,
        default="PLANNED"
    )

    summary = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    asset = relationship(
        "Asset",
        foreign_keys=[asset_id]
    )

    performed_by_user = relationship(
        "User",
        foreign_keys=[performed_by]
    )
