from unittest.mock import patch

from services.movie_recommendation_service import (
    get_movie_recommendations_with_fallback,
)


def test_movie_recommendation_uses_tmdb():
    movies = get_movie_recommendations_with_fallback(
        "3 Idiots",
        limit=1,
    )

    assert movies
    assert movies[0].title == "3 Idiots"
    assert movies[0].category == "movie"


def test_movie_recommendation_falls_back_to_sqlite():
    with patch(
        "services.movie_recommendation_service.get_movie_recommendations",
        side_effect=ConnectionError("Simulated TMDB failure"),
    ):
        movies = get_movie_recommendations_with_fallback(
            "3 Idiots",
            limit=1,
        )

    assert movies
    assert movies[0].title == "3 Idiots"
    assert movies[0].category == "movie"
