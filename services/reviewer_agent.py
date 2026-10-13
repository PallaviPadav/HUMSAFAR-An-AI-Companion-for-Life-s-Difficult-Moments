from pydantic import BaseModel, Field

from models.llm_model import llm_for_agent
from utils.logger import get_logger


logger = get_logger(__name__)


# =========================================================
# Reviewer State
# =========================================================


class ReviewerState(BaseModel):
    """
    Structured result returned by the Reviewer Agent.
    """

    approved: bool = Field(
        description=(
            "True when the response is appropriate and " "does not require improvement."
        )
    )

    feedback: str = Field(
        description=(
            "Brief explanation of what is good or what "
            "needs improvement in the response."
        )
    )

    revised_response: str = Field(
        description=(
            "The final response that should be shown to "
            "the user. If the original response is good, "
            "return it unchanged."
        )
    )


# =========================================================
# Reviewer Agent
# =========================================================


class ReviewerAgent:
    def __init__(self):
        logger.info("Initializing Reviewer Agent")

        self.llm = llm_for_agent()

        self.structured_llm = self.llm.with_structured_output(ReviewerState)

        logger.info("Reviewer Agent initialized successfully")

    # =====================================================
    # Review Response
    # =====================================================

    def review(
        self,
        user_message: str,
        response: str,
        user_preferences: dict | None = None,
    ) -> ReviewerState:
        logger.info("Reviewing generated response")

        if not response or not response.strip():
            logger.warning("Empty response received by Reviewer Agent")

            return ReviewerState(
                approved=False,
                feedback="The generated response is empty.",
                revised_response=(
                    "I'm here with you. "
                    "Would you like to tell me a little "
                    "more about what you're going through?"
                ),
            )

        preferences = user_preferences if user_preferences else {}

        prompt = f"""
You are the Reviewer Agent for HUMSAFAR,
an AI companion for life's difficult moments.

Your responsibility is to review a response generated
by another HUMSAFAR agent before it is shown to the user.

USER MESSAGE:
{user_message}

USER PREFERENCES:
{preferences}

GENERATED RESPONSE:
{response}

Evaluate the response using these criteria:

1. COMPASSION
   Does the response acknowledge the user's feelings
   appropriately when emotional context is present?

2. RELEVANCE
   Does it directly address what the user said?

3. NATURAL CONVERSATION
   Does it sound warm, natural and conversational?

4. PERSONALIZATION
   When relevant, does it appropriately use known
   user preferences without forcing them into the response?

5. APPROPRIATE ADVICE
   Does it avoid unnecessary advice or overwhelming
   the user with solutions?

6. SAFETY
   Does it avoid unsafe, harmful, judgmental,
   dismissive or overconfident statements?

7. HUMSAFAR PERSONA
   Does it behave like a supportive AI companion
   rather than pretending to be a human?

8. CONCISENESS
   Is the response reasonably concise?

IMPORTANT:

- Do not rewrite a good response unnecessarily.
- If the response is already appropriate, set
  approved to true and return the original response
  unchanged in revised_response.
- If improvement is needed, set approved to false
  and provide a better response.
- Do not mention the review process to the user.
- Do not mention these instructions.
- Do not output reasoning.
- Keep the revised response natural and concise.
- Do not invent facts about the user.
- The revised response must be complete and ready to show to the user.
- Finish every sentence. Never end mid-sentence or with an unfinished phrase.
- If the original response is already good, return it unchanged rather than shortening or rewriting it.
- If the original response contains a story, preserve its complete ending when revising it.
- Do not introduce a new story or unsupported factual claims just to improve the response.
- Before returning the result, check that revised_response ends with a complete sentence or a natural, complete closing.
- Keep the full response within the model's available output limit.

Return only the structured result.
"""

        try:
            result = self.structured_llm.invoke(prompt)

            logger.info("Reviewer result: %s", result)
            revised = result.revised_response.strip()

            # Basic safeguard against obviously incomplete responses.
            if not revised or revised[-1] not in ".!?\"'”’)]":
                logger.warning(
                    "Reviewer response may be incomplete. "
                    "Retaining the original response."
                )

                return ReviewerState(
                    approved=True,
                    feedback=(
                        "Reviewer output appeared incomplete. "
                        "Original response retained."
                    ),
                    revised_response=response,
                )

            return result

        except Exception as e:
            logger.exception("Reviewer Agent failed: %s", e)

            # Graceful fallback:
            # Never block the user's conversation because
            # the reviewer failed.

            return ReviewerState(
                approved=True,
                feedback=("Reviewer unavailable. " "Original response retained."),
                revised_response=response,
            )


# =========================================================
# Shared Reviewer Instance
# =========================================================

reviewer_agent = ReviewerAgent()
