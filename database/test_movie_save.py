from services.tmdb_service import get_movie_recommendations
from database.movie_repository import save_movie


def main():
    movies = get_movie_recommendations("3 Idiots", limit=1)

    if not movies:
        print("No movies found.")
        return

    movie = movies[0]

    print("TMDB movie:")
    print("TITLE:", movie.title)
    print("RATING:", movie.rating)
    print("IMAGE:", movie.image_url)

    save_movie(
        movie=movie,
        tmdb_id=20453,
    )

    print("Movie saved to SQLite successfully.")


if __name__ == "__main__":
    main()
