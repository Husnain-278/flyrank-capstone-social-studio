import httpx

from flyrank_capstone_social_studio.core.config import settings
from flyrank_capstone_social_studio.publishers.base import (
    PublishResult,
    SocialPublisher,
)


class TelegramPublisher(SocialPublisher):
    async def publish(
        self,
        *,
        content: str,
        idempotency_key: str,
    ) -> PublishResult:
        url = (
            f"https://api.telegram.org/bot"
            f"{settings.telegram_bot_token}/sendMessage"
        )

        payload = {
            "chat_id": settings.telegram_chat_id,
            "text": content,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
            )

        response.raise_for_status()

        data = response.json()

        if not data.get("ok"):
            raise RuntimeError(
                f"Telegram publishing failed: {data}"
            )

        message_id = data["result"]["message_id"]

        return PublishResult(
            external_id=str(message_id),
            platform="telegram",
        )