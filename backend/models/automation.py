from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Integer,
    String,
    Text,
)

from backend.config.database import Base


class AutomationLog(Base):
    __tablename__ = "automation_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    automation_name = Column(
        String(150),
        nullable=False,
        index=True,
    )

    execution_time = Column(
        DateTime,
        nullable=False,
    )

    status = Column(
        Enum(
            "SUCCESS",
            "FAILED",
        ),
        nullable=False,
    )

    input_source = Column(
        String(255),
        nullable=True,
    )

    output_summary = Column(
        Text,
        nullable=True,
    )

    output_data = Column(
        Text,
        nullable=True,
    )

    error_message = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )
