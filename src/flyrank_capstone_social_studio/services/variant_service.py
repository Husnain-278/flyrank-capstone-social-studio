from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from flyrank_capstone_social_studio.models.post import Post
from flyrank_capstone_social_studio.models.variant import (
    Platform,
    Variant,
    VariantStatus,
)
from flyrank_capstone_social_studio.services.constraint_service import (
    ConstraintService,
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


    

    @staticmethod
    async def approve(
        db: AsyncSession,
        post_id: UUID,
        variant_id: UUID,
    ) -> Variant:
        variant = await VariantService.get_variant(
            db=db,
            post_id=post_id,
            variant_id=variant_id,
        )

        if variant.status != VariantStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only draft variants can be approved.",
            )

        variant.status = VariantStatus.APPROVED

        await db.commit()
        await db.refresh(variant)

        return variant




    @staticmethod
    async def reject(
        db: AsyncSession,
        post_id: UUID,
        variant_id: UUID,
    ) -> Variant:
        variant = await VariantService.get_variant(
            db=db,
            post_id=post_id,
            variant_id=variant_id
        )

        if variant.status != VariantStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only draft variants can be rejected.",
            )

        variant.status = VariantStatus.REJECTED

        await db.commit()
        await db.refresh(variant)

        return variant




    @staticmethod
    async def edit(
        db: AsyncSession,
        post_id: UUID,
        variant_id: UUID,
        content: str,
    ) -> Variant:
        variant = await VariantService.get_variant(
            db=db,
            post_id=post_id, 
            variant_id=variant_id,
        )

        if variant.status != VariantStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only draft variants can be edited.",
            )

        ConstraintService.validate(
            content=content,
            platform=variant.platform,
        )

        variant.content = content

        await db.commit()
        await db.refresh(variant)

        return variant




    @staticmethod
    async def get_variant(
        db: AsyncSession,
        post_id: UUID,
        variant_id: UUID,
    ) -> Variant:
        result = await db.execute(
            select(Variant).where(
                Variant.id == variant_id,
                Variant.post_id == post_id,
            )
        )

        variant = result.scalar_one_or_none()

        if variant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Variant not found.",
            )

        return variant