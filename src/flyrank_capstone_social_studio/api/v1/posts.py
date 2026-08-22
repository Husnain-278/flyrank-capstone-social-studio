from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from flyrank_capstone_social_studio.core.database import get_db
from flyrank_capstone_social_studio.schemas.post import (
    PostCreateFromMarkdown,
    PostResponse,
)
from flyrank_capstone_social_studio.services.post_service import PostService
from uuid import UUID



from fastapi import HTTPException
from sqlalchemy import select

from flyrank_capstone_social_studio.models.post import Post
from flyrank_capstone_social_studio.schemas.variant import (
    VariantGenerateRequest,
    VariantResponse,
)
from flyrank_capstone_social_studio.services.generation_service import (
    GenerationService,
)
from flyrank_capstone_social_studio.services.variant_service import (
    VariantService,
)


from flyrank_capstone_social_studio.services.constraint_service import (
    ConstraintService,
    ConstraintValidationError,
)





router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


@router.post(
    "/markdown",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post_from_markdown(
    payload: PostCreateFromMarkdown,
    db: AsyncSession = Depends(get_db),
) -> PostResponse:
    post = await PostService.create_from_markdown(
        db=db,
        content=payload.content,
    )

    return post





@router.post(
    "/{post_id}/variants",
    response_model=VariantResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_variant(
    post_id: UUID,
    payload: VariantGenerateRequest,
    db: AsyncSession = Depends(get_db),
) -> VariantResponse:
    result = await db.execute(
        select(Post).where(Post.id == post_id)
    )

    post = result.scalar_one_or_none()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    generation_service = GenerationService()

    content = await generation_service.generate(
        post=post,
        platform=payload.platform,
    )

    try:
        ConstraintService.validate(
            content=content,
            platform=payload.platform,
        )
    except ConstraintValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        )

    variant = await VariantService.create(
        db=db,
        post=post,
        platform=payload.platform,
        content=content,
    )

    return variant