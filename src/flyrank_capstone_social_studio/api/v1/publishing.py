from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from flyrank_capstone_social_studio.core.database import get_db
from flyrank_capstone_social_studio.schemas.publish_attempt import (
    PublishAttemptResponse,
)
from flyrank_capstone_social_studio.services.publishing_service import (
    PublishingService,
)

router = APIRouter(
    prefix="/schedule-slots",
    tags=["Publishing"],
)


@router.post(
    "/{schedule_slot_id}/publish",
    response_model=PublishAttemptResponse,
    status_code=status.HTTP_200_OK,
)
async def publish_schedule_slot(
    schedule_slot_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> PublishAttemptResponse:
    return await PublishingService.publish(
        db=db,
        schedule_slot_id=schedule_slot_id,
    )