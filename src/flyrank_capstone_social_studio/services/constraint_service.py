import re

from flyrank_capstone_social_studio.core.platforms import (
    CONSTRAINT_PROFILES,
)
from flyrank_capstone_social_studio.models.variant import Platform


class ConstraintValidationError(Exception):
    pass


class ConstraintService:
    @staticmethod
    def validate(
        content: str,
        platform: Platform,
    ) -> None:
        profile = CONSTRAINT_PROFILES[platform]

        if len(content) > profile.max_length:
            raise ConstraintValidationError(
                f"Content exceeds the maximum length of "
                f"{profile.max_length} characters."
            )

        hashtags = re.findall(
            r"(?<!\w)#\w+",
            content,
        )

        if len(hashtags) > profile.max_hashtags:
            raise ConstraintValidationError(
                f"Content contains {len(hashtags)} hashtags. "
                f"Maximum allowed is {profile.max_hashtags}."
            )