import asyncio
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from flyrank_capstone_social_studio.core.celery import celery_app
from flyrank_capstone_social_studio.core.config import settings
from flyrank_capstone_social_studio.models.publish_attempt import (
    PublishAttempt,
    PublishAttemptStatus,
)
from flyrank_capstone_social_studio.models.schedule_slot import (
    ScheduleSlot,
    ScheduleStatus,
)
from flyrank_capstone_social_studio.services.publishing_service import (
    PublishingService,
)


@celery_app.task
def check_due_schedule_slots() -> None:
    asyncio.run(_check_due_schedule_slots())


async def _check_due_schedule_slots() -> None:
    engine = create_async_engine(settings.database_url)

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    try:
        async with session_factory() as db:
            statement = select(ScheduleSlot.id).where(
                ScheduleSlot.status == ScheduleStatus.PENDING,
                ScheduleSlot.scheduled_for
                <= datetime.now(timezone.utc),
            )

            result = await db.execute(statement)

            schedule_slot_ids = result.scalars().all()

            claimed_slot_ids = []

            for schedule_slot_id in schedule_slot_ids:
                claim_statement = (
                    update(ScheduleSlot)
                    .where(
                        ScheduleSlot.id == schedule_slot_id,
                        ScheduleSlot.status
                        == ScheduleStatus.PENDING,
                    )
                    .values(
                        status=ScheduleStatus.PROCESSING,
                        processing_started_at=datetime.now(
                            timezone.utc
                        ),
                    )
                )

                claim_result = await db.execute(
                    claim_statement
                )

                if claim_result.rowcount == 1:
                    claimed_slot_ids.append(
                        schedule_slot_id
                    )

            await db.commit()

        for schedule_slot_id in claimed_slot_ids:
            publish_schedule_slot.delay(
                str(schedule_slot_id)
            )

    finally:
        await engine.dispose()


@celery_app.task
def publish_schedule_slot(
    schedule_slot_id: str,
) -> None:
    asyncio.run(
        _publish_schedule_slot(
            UUID(schedule_slot_id)
        )
    )


async def _publish_schedule_slot(
    schedule_slot_id: UUID,
) -> None:
    engine = create_async_engine(settings.database_url)

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    try:
        async with session_factory() as db:
            schedule_slot = await db.get(
                ScheduleSlot,
                schedule_slot_id,
            )

            if schedule_slot is None:
                return

            if (
                schedule_slot.status
                != ScheduleStatus.PROCESSING
            ):
                return

            await PublishingService.publish(
                db=db,
                schedule_slot_id=schedule_slot.id,
            )

            schedule_slot.status = (
                ScheduleStatus.PUBLISHED
            )

            schedule_slot.processing_started_at = None

            await db.commit()

            print(
                f"Schedule slot published: "
                f"{schedule_slot.id}"
            )

    finally:
        await engine.dispose()


@celery_app.task
def recover_stuck_schedule_slots() -> None:
    asyncio.run(_recover_stuck_schedule_slots())


async def _recover_stuck_schedule_slots() -> None:
    engine = create_async_engine(settings.database_url)

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    try:
        async with session_factory() as db:
            recovery_threshold = (
                datetime.now(timezone.utc)
                - timedelta(
                    seconds=(
                        settings.schedule_recovery_timeout_seconds
                    )
                )
            )

            statement = select(ScheduleSlot).where(
                ScheduleSlot.status
                == ScheduleStatus.PROCESSING,
                or_(
                    ScheduleSlot.processing_started_at.is_(None),
                    ScheduleSlot.processing_started_at
                    <= recovery_threshold,
                ),
            )

            result = await db.execute(statement)

            schedule_slots = result.scalars().all()

            for schedule_slot in schedule_slots:
                statement = select(PublishAttempt).where(
                    PublishAttempt.schedule_slot_id
                    == schedule_slot.id
                )

                result = await db.execute(statement)

                publish_attempt = result.scalar_one_or_none()

                if (
                    publish_attempt is not None
                    and publish_attempt.status
                    == PublishAttemptStatus.SUCCESS
                ):
                    schedule_slot.status = (
                        ScheduleStatus.PUBLISHED
                    )

                    schedule_slot.processing_started_at = None

                    print(
                        "Recovered successful schedule slot: "
                        f"{schedule_slot.id}"
                    )

                elif publish_attempt is None:
                    schedule_slot.status = (
                        ScheduleStatus.PENDING
                    )

                    schedule_slot.processing_started_at = None

                    print(
                        "Recovered unstarted schedule slot: "
                        f"{schedule_slot.id}"
                    )

                elif (
                    publish_attempt.status
                    == PublishAttemptStatus.FAILED
                ):
                    schedule_slot.status = (
                        ScheduleStatus.PENDING
                    )

                    schedule_slot.processing_started_at = None

                    print(
                        "Recovered failed schedule slot: "
                        f"{schedule_slot.id}"
                    )

            await db.commit()

    finally:
        await engine.dispose()