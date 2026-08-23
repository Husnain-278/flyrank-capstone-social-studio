from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from flyrank_capstone_social_studio.models.publish_attempt import (
    PublishAttempt,
    PublishAttemptStatus,
)
from flyrank_capstone_social_studio.models.schedule_slot import (
    ScheduleSlot,
)
from flyrank_capstone_social_studio.publishers.factory import (
    PublisherFactory,
)


class PublishingService:
    @staticmethod
    async def publish(
        db: AsyncSession,
        schedule_slot_id: UUID,
    ) -> PublishAttempt:
        statement = (
            select(ScheduleSlot)
            .where(ScheduleSlot.id == schedule_slot_id)
            .options(
                selectinload(ScheduleSlot.variant)
            )
        )

        result = await db.execute(statement)

        schedule_slot = result.scalar_one_or_none()

        if schedule_slot is None:
            raise ValueError("Schedule slot not found.")

        variant = schedule_slot.variant

        idempotency_key = (
            f"publish:{variant.id}:{schedule_slot.id}"
        )

        statement = select(PublishAttempt).where(
            PublishAttempt.idempotency_key == idempotency_key
        )

        result = await db.execute(statement)

        existing_attempt = result.scalar_one_or_none()

        if (
            existing_attempt is not None
            and existing_attempt.status
            == PublishAttemptStatus.SUCCESS
        ):
            return existing_attempt

        if existing_attempt is None:
            publish_attempt = PublishAttempt(
                schedule_slot_id=schedule_slot.id,
                idempotency_key=idempotency_key,
                platform=variant.platform,
                content=variant.content,
                status=PublishAttemptStatus.PENDING,
            )

            db.add(publish_attempt)

            await db.commit()
            await db.refresh(publish_attempt)

        else:
            publish_attempt = existing_attempt

        try:
            publisher = PublisherFactory.get_publisher(
                variant.platform,
            )

            publish_result = await publisher.publish(
                content=variant.content,
                idempotency_key=idempotency_key,
            )

            publish_attempt.status = (
                PublishAttemptStatus.SUCCESS
            )

            publish_attempt.external_id = (
                publish_result.external_id
            )

            publish_attempt.error_message = None

            await db.commit()
            await db.refresh(publish_attempt)

            return publish_attempt

        except Exception as exc:
            publish_attempt.status = (
                PublishAttemptStatus.FAILED
            )

            publish_attempt.error_message = str(exc)

            await db.commit()
            await db.refresh(publish_attempt)

            raise