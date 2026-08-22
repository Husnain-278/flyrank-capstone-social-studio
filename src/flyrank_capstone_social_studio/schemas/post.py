from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class PostCreateFromMarkdown(BaseModel):
    content: str = Field(
        min_length=1,
        description="Blog post content in Markdown format.",
    )


class PostCreateFromURL(BaseModel):
    url: HttpUrl


class PostResponse(BaseModel):
    id: UUID
    source_url: str | None
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }