from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from flyrank_capstone_social_studio.core.database import Base
from flyrank_capstone_social_studio.models.variant import Platform


class PublishAttemptStatus(StrEnum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class PublishAttempt(Base):
    __tablename__ = "publish_attempts"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    schedule_slot_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "schedule_slots.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    platform: Mapped[Platform] = mapped_column(
        String(50),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[PublishAttemptStatus] = mapped_column(
        String(50),
        default=PublishAttemptStatus.PENDING,
        nullable=False,
    )

    external_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    schedule_slot = relationship(
        "ScheduleSlot",
        back_populates="publish_attempts",
    )