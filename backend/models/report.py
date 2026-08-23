from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
)

from backend.config.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    report_id = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    report_type = Column(
        String(100),
        nullable=False,
        index=True,
    )

    generated_by = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    generated_at = Column(
        DateTime,
        nullable=False,
    )

    file_name = Column(
        String(255),
        nullable=True,
    )

    file_path = Column(
        String(500),
        nullable=True,
    )

    status = Column(
        Enum(
            "GENERATED",
            "FAILED",
        ),
        nullable=False,
        default="GENERATED",
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )
