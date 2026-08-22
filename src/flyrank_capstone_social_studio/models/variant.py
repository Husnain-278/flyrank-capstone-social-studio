from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from flyrank_capstone_social_studio.core.database import Base


class Platform(StrEnum):
    TELEGRAM = "telegram"
    X = "x"


class VariantStatus(StrEnum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"


class Variant(Base):
    __tablename__ = "variants"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    post_id: Mapped[UUID] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
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

    status: Mapped[VariantStatus] = mapped_column(
        String(50),
        default=VariantStatus.DRAFT,
        nullable=False,
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

    post = relationship(
        "Post",
        back_populates="variants",
    )

    schedule_slots = relationship(
        "ScheduleSlot",
        back_populates="variant",
        cascade="all, delete-orphan",
        )