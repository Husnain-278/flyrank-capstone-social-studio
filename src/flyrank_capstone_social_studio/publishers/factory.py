from flyrank_capstone_social_studio.models.variant import Platform
from flyrank_capstone_social_studio.publishers.base import SocialPublisher
from flyrank_capstone_social_studio.publishers.mock_linkedin import (
    MockLinkedInPublisher,
)
from flyrank_capstone_social_studio.publishers.mock_x import MockXPublisher
from flyrank_capstone_social_studio.publishers.telegram import (
    TelegramPublisher,
)


class PublisherFactory:
    @staticmethod
    def get_publisher(
        platform: Platform,
    ) -> SocialPublisher:
        publishers: dict[
            Platform,
            type[SocialPublisher],
        ] = {
            Platform.TELEGRAM: TelegramPublisher,
            Platform.X: MockXPublisher,
            Platform.LINKEDIN: MockLinkedInPublisher,
        }

        publisher_class = publishers.get(platform)

        if publisher_class is None:
            raise ValueError(
                f"Unsupported platform: {platform}"
            )

        return publisher_class()