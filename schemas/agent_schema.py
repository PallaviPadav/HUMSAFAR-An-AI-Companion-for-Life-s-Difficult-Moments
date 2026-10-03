from typing import Literal
from pydantic import BaseModel, Field


class AgentDecision(BaseModel):
    agent: Literal[
        "conversation", "hobby", "activities", "recommendation", "inspirational"
    ] = Field(description="The specialist agent that should handle the user's request.")

    task_state: Literal["in_progress", "completed"] = Field(
        description="Whether the current user task is still in progress or completed."
    )

    reason: str = Field(
        description="Explain why this agent was selected and why the task "
        "is in progress or completed."
    )
