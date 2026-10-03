from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    """
    Structured input for recommendation requests.
    """

    recommendation_type: str = Field(
        description=(
            "Type of recommendation requested by the user. "
            "Examples: movie, music, travel, game."
        )
    )

    preferences: str = Field(
        description=(
            "User preferences or requirements for the recommendation. "
            "Include genre, mood, location, language, budget, etc. "
            "when provided by the user."
        )
    )
