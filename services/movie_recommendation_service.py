from services.tmdb_service import get_movie_recommendations
from database.movie_repository import get_movie_by_title
from schemas.recommendation_schema import RecommendationItem
import sys


def get_movie_recommendations_with_fallback(
    query: str,
    limit: int = 5,
):
    """
    Get movie recommendations from TMDB first.
    Fall back to SQLite if TMDB is unavailable.

    Both sources return RecommendationItem objects.
    """

    try:
        movies = get_movie_recommendations(query, limit=limit)

        if movies:
            return movies

    except Exception as e:
        print(f"TMDB unavailable: {e}", file=sys.stderr)
        print("Falling back to SQLite...", file=sys.stderr)

    # SQLite fallback
    movie = get_movie_by_title(query)

    if movie:
        recommendation = RecommendationItem(
            title=movie["title"],
            description=movie["description"] or "No description available.",
            category="movie",
            image_url=movie["poster_url"],
            video_url=movie["video_url"],
            details_url=movie["details_url"],
            rating=movie["rating"],
        )

        return [recommendation]

    return []
