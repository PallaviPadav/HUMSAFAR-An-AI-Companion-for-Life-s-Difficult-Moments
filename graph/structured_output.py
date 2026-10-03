from graph.state import ConversationState
import os
from dotenv import load_dotenv
from schemas.agent_schema import AgentDecision
from schemas.recommendation_query_schema import RecommendationQuery
from schemas.movie_recommendation_schema import (
    MovieRecommendationSelection,
)
from models.llm_model import llm_for_agent
from utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

key = os.getenv("GROQ_API_KEY")

if not key:
    raise ValueError("GROQ_API_KEY is not set in the environment.")

# =========================================================
# LLM
# =========================================================

llm = llm_for_agent()
"""ChatGroq(
    model="qwen/qwen3.8-27b",
    temperature=0.4,
    api_key=key,
    max_tokens=800,
    reasoning_effort="none",
)"""
logger.info("Set LLM for structured output")

structured_llm = llm.with_structured_output(AgentDecision)
recommendation_query_llm = llm.with_structured_output(RecommendationQuery)
movie_recommendation_selection_llm = llm.with_structured_output(
    MovieRecommendationSelection
)
