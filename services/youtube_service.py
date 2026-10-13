import os

import httpx
from dotenv import load_dotenv

from utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"


def search_inspirational_videos(
    query: str,
    limit: int = 5,
) -> list[dict]:
    """
    Search YouTube for short inspirational videos.

    Returns a list of dictionaries containing:
    - video_id
    - title
    - description
    - channel
    - thumbnail
    - video_url
    - embed_url
    """

    if not YOUTUBE_API_KEY:
        raise ValueError("YOUTUBE_API_KEY is missing from the .env file.")

    if not query or not query.strip():
        raise ValueError("Please provide a search query.")

    # Keep the number of results within YouTube's
    # supported maxResults range.
    limit = max(1, min(limit, 50))

    params = {
        "part": "snippet",
        "q": query.strip(),
        "type": "video",
        "maxResults": limit,
        "videoDuration": "short",
        "videoEmbeddable": "true",
        "relevanceLanguage": "en",
        "regionCode": "IN",
        "safeSearch": "moderate",
        "order": "relevance",
        "key": YOUTUBE_API_KEY,
    }

    logger.info(
        "Searching YouTube for inspirational videos: %s",
        query,
    )

    try:
        response = httpx.get(
            YOUTUBE_SEARCH_URL,
            params=params,
            timeout=20.0,
        )
        response.raise_for_status()

        data = response.json()
        videos = []

        for item in data.get("items", []):
            video_id = item.get("id", {}).get("videoId")

            snippet = item.get("snippet", {})

            # Skip results without a usable video ID.
            if not video_id:
                continue

            thumbnails = snippet.get("thumbnails", {})

            thumbnail = (
                thumbnails.get("high")
                or thumbnails.get("medium")
                or thumbnails.get("default")
                or {}
            )

            videos.append(
                {
                    "video_id": video_id,
                    "title": snippet.get("title", "Untitled video"),
                    "description": snippet.get("description", ""),
                    "channel": snippet.get("channelTitle", "Unknown channel"),
                    "thumbnail": thumbnail.get("url"),
                    "video_url": (f"https://www.youtube.com/watch?v={video_id}"),
                    "embed_url": (f"https://www.youtube.com/embed/{video_id}"),
                }
            )

        logger.info(
            "YouTube returned %d usable videos",
            len(videos),
        )

        return videos

    except httpx.HTTPStatusError as e:
        logger.error(
            "YouTube API returned HTTP status %s: %s",
            e.response.status_code,
            e.response.text,
        )
        raise

    except httpx.RequestError as e:
        logger.error(
            "Unable to connect to YouTube API: %s",
            e,
        )
        raise


if __name__ == "__main__":
    results = search_inspirational_videos(
        query="motivational stories overcoming failure",
        limit=5,
    )

    for index, video in enumerate(results, start=1):
        print(f"\nVideo {index}")
        print("Title:", video["title"])
        print("Channel:", video["channel"])
        print("Description:", video["description"])
        print("URL:", video["video_url"])
        print("Thumbnail:", video["thumbnail"])
