from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ScheduleSlotCreate(BaseModel):
    scheduled_for: datetime


class ScheduleSlotResponse(BaseModel):
    id: UUID
    variant_id: UUID
    scheduled_for: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }