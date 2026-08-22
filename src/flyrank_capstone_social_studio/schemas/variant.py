from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import BaseModel, Field

from flyrank_capstone_social_studio.models.variant import (
    Platform,
    VariantStatus,
)


class VariantGenerateRequest(BaseModel):
    platform: Platform





class VariantUpdateRequest(BaseModel):
    content: str = Field(
        min_length=1,
    )




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



