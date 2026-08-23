from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class PublishResult:
    external_id: str
    platform: str


class SocialPublisher(ABC):
    @abstractmethod
    async def publish(
        self,
        *,
        content: str,
        idempotency_key: str,
    ) -> PublishResult:
        """
        Publish content to a social media platform.
        """
        raise NotImplementedError