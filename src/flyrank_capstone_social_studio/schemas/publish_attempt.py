from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from flyrank_capstone_social_studio.models.publish_attempt import (
    PublishAttemptStatus,
)
from flyrank_capstone_social_studio.models.variant import Platform


class PublishAttemptResponse(BaseModel):
    id: UUID
    schedule_slot_id: UUID
    platform: Platform
    content: str
    status: PublishAttemptStatus
    external_id: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )