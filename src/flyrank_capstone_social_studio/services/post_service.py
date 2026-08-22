from sqlalchemy.ext.asyncio import AsyncSession

from flyrank_capstone_social_studio.models.post import Post


class PostService:
    @staticmethod
    async def create_from_markdown(
        db: AsyncSession,
        content: str,
    ) -> Post:
        post = Post(
            content=content,
            source_url=None,
        )

        db.add(post)

        await db.commit()
        await db.refresh(post)

        return post