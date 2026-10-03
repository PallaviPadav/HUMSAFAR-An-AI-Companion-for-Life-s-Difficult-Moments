import sqlite3
from pathlib import Path

from schemas.recommendation_schema import RecommendationItem


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "humsafar.db"


def save_movie(movie: RecommendationItem, tmdb_id: int, release_date: str = None):
    """
    Save a movie recommendation into the local SQLite database.
    """

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO movies (
            tmdb_id,
            title,
            description,
            rating,
            poster_url,
            video_url,
            details_url,
            genre,
            release_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            tmdb_id,
            movie.title,
            movie.description,
            movie.rating,
            movie.image_url,
            movie.video_url,
            movie.details_url,
            None,
            release_date,
        ),
    )

    connection.commit()
    connection.close()

    print(f"Movie saved: {movie.title}")


def get_movie_by_title(title: str):
    """
    Retrieve a movie from the local SQLite database by title.
    """

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            tmdb_id,
            title,
            description,
            rating,
            poster_url,
            video_url,
            details_url,
            genre,
            release_date
        FROM movies
        WHERE title = ?
        """,
        (title,),
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return dict(row)
