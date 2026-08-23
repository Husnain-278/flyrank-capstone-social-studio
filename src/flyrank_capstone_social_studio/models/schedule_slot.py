from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from flyrank_capstone_social_studio.core.database import Base


class ScheduleStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    PUBLISHED = "published"

class ScheduleSlot(Base):
    __tablename__ = "schedule_slots"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    variant_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "variants.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    scheduled_for: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    status: Mapped[ScheduleStatus] = mapped_column(
        String(50),
        default=ScheduleStatus.PENDING,
        nullable=False,
    )

    processing_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
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

    variant = relationship(
        "Variant",
        back_populates="schedule_slots",
    )

    publish_attempts = relationship(
        "PublishAttempt",
        back_populates="schedule_slot",
        cascade="all, delete-orphan",
    )