from uuid import uuid4

from flyrank_capstone_social_studio.publishers.base import (
    PublishResult,
    SocialPublisher,
)


class MockLinkedInPublisher(SocialPublisher):
    async def publish(
        self,
        *,
        content: str,
        idempotency_key: str,
    ) -> PublishResult:
        return PublishResult(
            external_id=str(uuid4()),
            platform="linkedin",
        )