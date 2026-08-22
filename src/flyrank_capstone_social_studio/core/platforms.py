from dataclasses import dataclass

from flyrank_capstone_social_studio.models.variant import Platform


@dataclass(frozen=True)
class ConstraintProfile:
    max_length: int
    tone: str
    max_hashtags: int


CONSTRAINT_PROFILES: dict[Platform, ConstraintProfile] = {
    Platform.TELEGRAM: ConstraintProfile(
        max_length=4096,
        tone="informative and engaging",
        max_hashtags=5,
    ),
    Platform.X: ConstraintProfile(
        max_length=280,
        tone="concise and engaging",
        max_hashtags=3,
    ),
}