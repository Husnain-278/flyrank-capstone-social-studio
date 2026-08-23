from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from flyrank_capstone_social_studio.models.schedule_slot import (
    ScheduleStatus,
)


class ScheduleSlotCreate(BaseModel):
    scheduled_for: datetime


class ScheduleSlotResponse(BaseModel):
    id: UUID
    variant_id: UUID
    scheduled_for: datetime
    status: ScheduleStatus
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }