from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from flyrank_capstone_social_studio.models.variant import (
    Platform,
    VariantStatus,
)


class VariantGenerateRequest(BaseModel):
    platform: Platform


class VariantResponse(BaseModel):
    id: UUID
    post_id: UUID
    platform: Platform
    content: str
    status: VariantStatus
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }