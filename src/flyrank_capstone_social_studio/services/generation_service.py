from langchain_core.messages import HumanMessage, SystemMessage
from langchain_mistralai import ChatMistralAI

from flyrank_capstone_social_studio.core.config import settings
from flyrank_capstone_social_studio.core.platforms import (
    CONSTRAINT_PROFILES,
)
from flyrank_capstone_social_studio.models.post import Post
from flyrank_capstone_social_studio.models.variant import Platform


class GenerationService:
    def __init__(self) -> None:
        self.llm = ChatMistralAI(
            model="mistral-small-2506",
            api_key=settings.mistral_api_key,
            temperature=0.5,
        )

    async def generate(
        self,
        post: Post,
        platform: Platform,
    ) -> str:
        profile = CONSTRAINT_PROFILES[platform]

        messages = [
            SystemMessage(
                content=(
                    "You are a social media content writer. "
                    "Generate content using only the provided source post. "
                    "Do not add facts, claims, or information that are not "
                    "present in the source post."
                )
            ),
            HumanMessage(
                content=(
                    f"Platform: {platform.value}\n"
                    f"Maximum length: {profile.max_length} characters\n"
                    f"Tone: {profile.tone}\n"
                    f"Maximum hashtags: {profile.max_hashtags}\n\n"
                    "Source post:\n"
                    f"{post.content}"
                )
            ),
        ]

        response = await self.llm.ainvoke(messages)

        return response.content.strip()