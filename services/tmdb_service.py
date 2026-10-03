import os
import httpx
from dotenv import load_dotenv

from schemas.recommendation_schema import RecommendationItem


load_dotenv()

TMDB_API_TOKEN = os.getenv("TMDB_API_KEY")

TMDB_BASE_URL = "https://api.themoviedb.org/3"

TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


def search_movies(query: str):
    """
    Search TMDB for movies matching the user's query.
    """

    url = f"{TMDB_BASE_URL}/search/movie"

    headers = {
        "Authorization": f"Bearer {TMDB_API_TOKEN}",
        "accept": "application/json",
    }

    params = {
        "query": query,
        "language": "en-US",
        "page": 1,
        "include_adult": False,
    }
    response = httpx.get(
        url,
        headers=headers,
        params=params,
        timeout=20.0,
    )

    response.raise_for_status()

    return response.json()


def get_movie_recommendations(query: str, limit: int = 5):
    """
    Search TMDB and convert the results into HUMSAFAR
    RecommendationItem objects.
    """

    data = search_movies(query)

    recommendations = []

    for movie in data.get("results", [])[:limit]:
        poster_path = movie.get("poster_path")

        image_url = None

        if poster_path:
            image_url = f"{TMDB_IMAGE_BASE_URL}{poster_path}"

        recommendation = RecommendationItem(
            title=movie.get("title", "Unknown"),
            description=movie.get("overview", "No description available."),
            category="movie",
            image_url=image_url,
            video_url=None,
            details_url=(f"https://www.themoviedb.org/movie/" f"{movie.get('id')}"),
            rating=movie.get("vote_average"),
        )

        recommendations.append(recommendation)

    return recommendations


def search_movie_candidates(query: str, limit: int = 10):
    """
    Search TMDB for movie candidates.

    The returned candidates include movie title and
    description. The description is later evaluated
    by the Movie Selection LLM.
    """

    data = search_movies(query)

    candidates = []

    for movie in data.get("results", [])[:limit]:
        candidates.append(
            {
                "id": movie.get("id"),
                "title": movie.get("title"),
                "overview": movie.get(
                    "overview",
                    "No description available.",
                ),
                "genre_ids": movie.get("genre_ids", []),
                "vote_average": movie.get("vote_average"),
                "vote_count": movie.get("vote_count"),
                "popularity": movie.get("popularity"),
                "poster_path": movie.get("poster_path"),
                "release_date": movie.get("release_date"),
            }
        )

    return candidates
