from typing_extensions import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing import Optional, Literal


class ConversationState(TypedDict, total=False):
    # =========================================
    # conversation
    # =========================================
    messages: Annotated[list[BaseMessage], add_messages]

    # =========================================
    # Gaurdrail
    # =========================================
    is_unsafe: bool
    has_emergency: bool
    has_prompt_injection: bool
    has_pii: bool
    safety_message: str

    # =========================================
    # Preference Memory
    # =========================================
    user_preferences: dict
    preference_updates: dict

    # =========================================
    # Agentic AI
    # =========================================
    current_intent: Optional[str]
    selected_agent: Optional[
        Literal[
            "conversation", "hobby", "activities", "recommendation", "inspirational"
        ]
    ]
    task_state: Literal["in_progress", "completed"]

    final_response: Optional[str]

    inspirational_videos: list[dict]
