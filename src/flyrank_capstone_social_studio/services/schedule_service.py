from datetime import datetime
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from flyrank_capstone_social_studio.models.schedule_slot import (
    ScheduleSlot,
)
from flyrank_capstone_social_studio.models.variant import (
    VariantStatus,
)
from flyrank_capstone_social_studio.services.variant_service import (
    VariantService,
)


class ScheduleService:
    @staticmethod
    async def create(
        db: AsyncSession,
        post_id: UUID,
        variant_id: UUID,
        scheduled_for: datetime,
    ) -> ScheduleSlot:
        variant = await VariantService.get_variant(
            db=db,
            post_id=post_id,
            variant_id=variant_id,
        )

        if variant.status != VariantStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only approved variants can be scheduled.",
            )

        schedule_slot = ScheduleSlot(
            variant_id=variant.id,
            scheduled_for=scheduled_for,
        )

        db.add(schedule_slot)

        await db.commit()
        await db.refresh(schedule_slot)

        return schedule_slot