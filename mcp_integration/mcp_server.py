import sys
from mcp.server.mcpserver import MCPServer

from services.movie_recommendation_service import (
    get_movie_recommendations_with_fallback,
)
from services.tmdb_service import search_movie_candidates
from services.youtube_service import (
    search_inspirational_videos as search_youtube_videos,
)

mcp = MCPServer(
    name="HUMSAFAR",
    version="1.0.0",
)


@mcp.tool()
def search_movies(query: str, limit: int = 5) -> list[dict]:
    """
    Search for movie candidates using TMDB.

    The candidates include:
    - movie titles
    - descriptions
    - ratings
    - genres
    - popularity
    - poster information

    If the original query does not return candidates,
    a broader motivational search is attempted.

    If TMDB is unavailable, the existing SQLite
    fallback is used.
    """

    try:
        # ---------------------------------------------------------
        # Step 1: Search TMDB using the user's extracted query
        # ---------------------------------------------------------
        candidates = search_movie_candidates(
            query=query,
            limit=limit,
        )

        # If TMDB returns candidates, use them.
        if candidates:
            return candidates

        # ---------------------------------------------------------
        # Step 2: Broad fallback search
        #
        # TMDB search is primarily title-oriented.
        # A conceptual query such as:
        #
        # "motivational happy ending"
        #
        # may return no movies.
        #
        # Therefore, retrieve a broader set of motivational
        # movies and allow the Recommendation Agent's LLM
        # to evaluate their titles and descriptions.
        # ---------------------------------------------------------
        candidates = search_movie_candidates(
            query="motivational",
            limit=limit,
        )

        if candidates:
            return candidates

    except Exception as e:
        print(f"TMDB candidate search failed: {e}")

    # -------------------------------------------------------------
    # Step 3: Existing SQLite fallback
    #
    # This is used if:
    # - TMDB is unavailable
    # - TMDB search fails
    # - no suitable TMDB candidates are returned
    # -------------------------------------------------------------
    movies = get_movie_recommendations_with_fallback(
        query=query,
        limit=limit,
    )

    return [movie.model_dump() for movie in movies]


@mcp.tool()
def search_inspirational_videos(
    query: str,
    limit: int = 5,
) -> list[dict]:
    """
    Search YouTube for short inspirational videos.

    Returns video titles, descriptions, channel names,
    thumbnails, YouTube links and embed links.

    This tool can help HUMSAFAR find videos relevant
    to the user's situation, such as interview setbacks,
    career challenges, self-doubt or personal growth.
    """

    try:
        videos = search_youtube_videos(
            query=query,
            limit=limit,
        )

        if videos:
            return videos

        return search_youtube_videos(
            query="inspirational stories overcoming challenges",
            limit=limit,
        )

    except Exception as e:
        print(
            f"YouTube inspirational search failed: {e}",
            file=sys.stderr,
        )
        raise


if __name__ == "__main__":
    import asyncio

    asyncio.run(mcp.run_stdio_async())
