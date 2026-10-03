from typing import Literal, Optional
from pydantic import BaseModel, Field


class RecommendationItem(BaseModel):
    """
    Structured recommendation data returned to the HUMSAFAR UI.
    """

    title: str = Field(description="Name of the recommended item.")

    description: str = Field(description="Short description of the recommendation.")

    category: Literal[
        "movie",
        "music",
        "travel",
        "game",
    ] = Field(description="Type of recommendation.")

    image_url: Optional[str] = Field(
        default=None,
        description="URL of the image, poster, album art, or destination image.",
    )

    video_url: Optional[str] = Field(
        default=None,
        description="URL of a trailer, music video, travel video, or related video.",
    )

    details_url: Optional[str] = Field(
        default=None, description="URL containing additional information."
    )

    rating: Optional[float] = Field(default=None, description="Rating when available.")


class RecommendationResponse(BaseModel):
    """
    Complete recommendation response returned by the Recommendation Agent.
    """

    category: Literal[
        "movie",
        "music",
        "travel",
        "game",
    ]

    message: str = Field(
        description="Short natural-language explanation from HUMSAFAR."
    )

    recommendations: list[RecommendationItem] = Field(
        description="List of recommended items."
    )
