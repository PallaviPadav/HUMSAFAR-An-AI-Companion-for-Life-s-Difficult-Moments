from typing import List
from pydantic import BaseModel, Field
from utils.logger import get_logger
from models.llm_model import llm_for_agent

logger = get_logger(__name__)

# =========================================================
# Structured Preference Schema
# =========================================================


class PreferenceExtractionState(BaseModel):
    """
    Represents stable user preferences extracted
    from a conversation message.
    """

    has_preferences: bool = Field(
        description=(
            "True only when the message contains a stable "
            "preference, interest, hobby, dislike, activity "
            "preference, or communication preference."
        )
    )

    hobbies: List[str] = Field(
        default_factory=list,
        description="User's hobbies that appear to be stable preferences.",
    )

    activities: List[str] = Field(
        default_factory=list, description="Activities the user enjoys or prefers."
    )

    interests: List[str] = Field(
        default_factory=list,
        description="Topics or areas the user is genuinely interested in.",
    )

    favorite_categories: List[str] = Field(
        default_factory=list,
        description="Preferred categories such as movies, books, music, travel, etc.",
    )

    dislikes: List[str] = Field(
        default_factory=list,
        description="Things the user explicitly dislikes or prefers to avoid.",
    )

    communication_preferences: List[str] = Field(
        default_factory=list,
        description="How the user prefers HUMSAFAR to communicate.",
    )


# =========================================================
# Preference Extractor
# =========================================================


class PreferenceExtractor:
    def __init__(self):
        logger.info("Initializing Preference Extractor")

        self.llm = llm_for_agent()

        self.structured_llm = self.llm.with_structured_output(PreferenceExtractionState)

        logger.info("Preference Extractor initialized successfully")

    # =====================================================
    # Extract Preferences
    # =====================================================

    def extract(self, user_message: str) -> PreferenceExtractionState:
        logger.info("Extracting preference from user message: %s", user_message)

        if not user_message or not user_message.strip():
            logger.info("Empty message. No prefrence to extract.")
            return PreferenceExtractionState(has_preferences=False)

        prompt = f"""
        You are the preference extraction component of HUMSAFAR,
        an AI companion.

        Your task is to identify ONLY stable user preferences
        that are explicitly stated or strongly implied in the
        user's message.

        User message:
        "{user_message}"

        Extract information only when it could reasonably help
        HUMSAFAR personalize future conversations.

        IMPORTANT RULES:

        1. Do NOT treat every activity mentioned by the user
        as a preference.

        2. A one-time event should NOT be stored as a preference.

        Example:
        "I went for a walk yesterday."
        -> Do not store walking.

        3. A stable preference should be stored.

        Example:
        "I love going for walks."
        -> Store walking.

        4. Temporary emotional states are NOT preferences.

        Example:
        "Today I feel like watching a movie."
        -> Do not store movies as a preference.

        5. Explicit dislikes should be stored.

        Example:
        "I don't like crowded places."
        -> Store crowded places as a dislike.

        6. Communication preferences should be stored.

        Example:
        "Please keep your answers short."
        -> Store short responses.

        7. Do not infer preferences merely because
        something is mentioned.

        8. Do not invent information.

        9. Keep extracted preferences concise.

        10. If there are no stable preferences,
            set has_preferences to false and leave
            all lists empty.

        Return only the structured result.
        """
        try:
            result = self.structured_llm.invoke(prompt)

            logger.info("Preference extraction result: %s", result)

            return result

        except Exception as e:
            logger.exception("Preference extraction failed: %s", e)

            # Graceful fallback
            return PreferenceExtractionState(has_preferences=False)


# =========================================================
# Shared Extractor Instance
# =========================================================

preference_extractor = PreferenceExtractor()
