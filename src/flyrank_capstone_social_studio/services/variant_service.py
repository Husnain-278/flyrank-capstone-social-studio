from sqlalchemy.ext.asyncio import AsyncSession

from flyrank_capstone_social_studio.models.post import Post
from flyrank_capstone_social_studio.models.variant import (
    Platform,
    Variant,
)
from flyrank_capstone_social_studio.core.platforms import (
    CONSTRAINT_PROFILES,
)


class VariantService:
    @staticmethod
    async def create(
        db: AsyncSession,
        post: Post,
        platform: Platform,
        content: str,
    ) -> Variant:
        variant = Variant(
            post_id=post.id,
            platform=platform,
            content=content,
        )

        db.add(variant)

        await db.commit()
        await db.refresh(variant)

        return variant