from models.llm_model import llm_for_agent
from utils.logger import get_logger
import asyncio
from mcp_integration.mcp_client import search_movies_via_mcp
from graph.structured_output import (
    recommendation_query_llm,
    movie_recommendation_selection_llm,
)


logger = get_logger(__name__)


RECOMMENDATION_AGENT_PROMPT = """
You are HUMSAFAR's Recommendation Agent.

Your role is to suggest meaningful and enjoyable
recommendations based on the user's current feelings,
interests, preferences and situation.

You can recommend:

- Music or songs
- Books
- Movies
- Travel destinations
- Games
- Podcasts
- Creative content
- Other forms of entertainment or learning

Guidelines:

- Be warm, compassionate and encouraging.
- Understand the user's current message before making recommendations.
- Suggest only 2 or 3 recommendations at a time.
- Keep recommendations relevant to the user's request.
- Briefly explain why each recommendation may suit the user.
- Give the user freedom to choose.
- Do not overwhelm the user with a long list.
- Do not shame or pressure the user.
- Do not make medical or psychological diagnoses.
- Do not claim to be human.
- If the user has not specified a category clearly,
  ask a gentle follow-up question when necessary.

The goal is to gently help the user discover something
enjoyable, interesting or comforting.
"""


def recommendation_agent(user_message: str) -> str:
    logger.info("Recommendation Agent started")

    # --------------------------------------------------
    # STEP 1: Understand the user's recommendation request
    # --------------------------------------------------

    recommendation_query = recommendation_query_llm.invoke(user_message)

    logger.info(
        "Recommendation query extracted: category=%s, search_query=%s",
        recommendation_query.category,
        recommendation_query.search_query,
    )

    # --------------------------------------------------
    # MOVIE RECOMMENDATIONS THROUGH MCP
    # --------------------------------------------------

    if recommendation_query.category == "movie":
        logger.info("Movie recommendation request detected")
        logger.info("Calling movie recommendation through MCP")

        # --------------------------------------------------
        # Get movie candidates through MCP
        # --------------------------------------------------

        mcp_result = asyncio.run(
            search_movies_via_mcp(
                query=recommendation_query.search_query,
                limit=10,
            )
        )

        logger.info(
            "MCP movie result received: %s",
            mcp_result,
        )

        # --------------------------------------------------
        # Extract structured candidates from MCP result
        # --------------------------------------------------

        if mcp_result.is_error:
            logger.error(
                "MCP movie search failed: %s",
                mcp_result.content,
            )

            return {
                "category": "movie",
                "message": (
                    "I couldn't access movie recommendations right now. "
                    "Please try again in a moment."
                ),
                "recommendations": [],
            }

        structured_content = mcp_result.structured_content or {}

        candidates = structured_content.get(
            "result",
            [],
        )

        logger.info(
            "Number of movie candidates received: %d",
            len(candidates),
        )

        if not candidates:
            logger.warning(
                "No movie candidates found for query: %s",
                recommendation_query.search_query,
            )

            return {
                "category": "movie",
                "message": (
                    "I couldn't find suitable movies for "
                    "that request. Let me try a different "
                    "way."
                ),
                "recommendations": [],
            }

        # --------------------------------------------------
        # Prepare movie information for the LLM
        # --------------------------------------------------

        candidate_text = "\n\n".join(
            [
                (
                    f"Title: {movie.get('title')}\n"
                    f"Description: {movie.get('overview')}\n"
                    f"Rating: {movie.get('vote_average')}\n"
                    f"Vote Count: {movie.get('vote_count')}\n"
                    f"Genres: {movie.get('genre_ids')}"
                )
                for movie in candidates
            ]
        )

        selection_prompt = f"""
            You are HUMSAFAR's movie recommendation evaluator.

            The user's original request is:

            {user_message}

            The extracted movie search query is:

            {recommendation_query.search_query}

            Below are movie candidates retrieved through TMDB.

            Your task is to select the 2 or 3 movies that best
            match the user's original request.

            Evaluate BOTH the movie title and movie description.

            The movie description is especially important because
            the user's requested mood, theme, situation or purpose
            may not appear in the movie title.

            Consider:

            - The user's requested mood or theme
            - Whether the story appears motivational
            - Whether the story involves overcoming challenges
            - Whether the story could provide encouragement
            - Whether the ending appears positive when this is requested
            - Whether the movie is relevant to the user's situation
            - The overall relevance of the movie description

            Do not select a movie merely because its title
            contains a keyword.

            Use the movie description as the primary source
            for semantic relevance.

            Return only the structured output requested.

            MOVIE CANDIDATES:

            {candidate_text}
            """

        # --------------------------------------------------
        # LLM selects the most relevant movies
        # --------------------------------------------------

        selection = movie_recommendation_selection_llm.invoke(selection_prompt)

        logger.info(
            "Selected movie titles: %s",
            selection.selected_titles,
        )

        logger.info(
            "Movie selection reason: %s",
            selection.reason,
        )

        # --------------------------------------------------
        # Match selected titles back to original candidates
        # --------------------------------------------------

        selected_movies = []

        selected_titles_lower = {
            title.strip().lower() for title in selection.selected_titles
        }

        for movie in candidates:
            title = movie.get("title", "")

            if title.strip().lower() in selected_titles_lower:
                selected_movies.append(movie)

        logger.info(
            "Final selected movies: %s",
            [movie.get("title") for movie in selected_movies],
        )

        return {
            "category": "movie",
            "message": selection.reason,
            "recommendations": selected_movies,
        }

    # --------------------------------------------------
    # OTHER RECOMMENDATIONS
    # --------------------------------------------------

    messages = [
        {
            "role": "system",
            "content": RECOMMENDATION_AGENT_PROMPT,
        },
        {
            "role": "user",
            "content": user_message,
        },
    ]

    llm = llm_for_agent()
    response = llm.invoke(messages)

    logger.info("Recommendation Agent completed")

    return response.content
