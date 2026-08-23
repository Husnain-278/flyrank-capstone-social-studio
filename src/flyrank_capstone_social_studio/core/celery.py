from celery import Celery

from flyrank_capstone_social_studio.core.config import settings


celery_app = Celery(
    "social_media_studio",
    broker=settings.celery_broker_url,
    include=[
        "flyrank_capstone_social_studio.workers.tasks",
    ],
)


celery_app.conf.update(
    timezone=settings.timezone,
    enable_utc=True,
    beat_schedule={
        "check-due-schedule-slots": {
            "task": (
                "flyrank_capstone_social_studio."
                "workers.tasks.check_due_schedule_slots"
            ),
            "schedule": 10.0,
        },
        "recover-stuck-schedule-slots": {
            "task": (
                "flyrank_capstone_social_studio."
                "workers.tasks.recover_stuck_schedule_slots"
            ),
            "schedule": 30.0,
        },
    },
)