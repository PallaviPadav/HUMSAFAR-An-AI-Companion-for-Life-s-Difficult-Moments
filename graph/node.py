import os
import logging

from agents.activities_agent import activities_agent
from langchain_core.messages import SystemMessage
from utils.logger import get_logger
from guardrails.guardrails import (
    check_input,
    emergency_response,
    validate_output,
    safe_fallback,
)
from langchain_core.messages import AIMessage
from graph.state import ConversationState
from models.llm_model import llm_for_agent
from agents.conversation_agent import conversation_agent
from graph.supervisor import supervisor_agent
from agents.hobby_agent import hobby_agent
from agents.recommendation_agent import recommendation_agent
from agents.inspiration_agent import inspiration_agent
from langchain_core.runnables import RunnableConfig
from services.preference_memory import update_preferences
from services.reviewer_agent import reviewer_agent

logger = get_logger(__name__)


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
logger.info("Set LLM")

# =========================================================
# LOGGING
# =========================================================


# =========================================================
# HUMSAFAR SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """

You are HUMSAFAR,
an AI Companion for Life's Difficult Moments.

Your role is to:

- Listen without judgment and respond with compassion.
- Acknowledge the user's feelings.
- Encourage the user gently.
- Help the user reflect on their situation.
- Be warm, respectful and conversational.
- Never shame, mock or dismiss the user.
- Do not overwhelm the user with unnecessary advice.
- Ask thoughtful follow-up questions when appropriate.
- Keep responses concise and natural.
- Usually respond in 2 to 5 short paragraphs.
- Do not provide unnecessarily long explanations unless the user asks for detail.
- Return ONLY the final response to the user.
- NEVER output your reasoning or thinking process.
- NEVER output <think>, </think>, analysis, reasoning, or internal deliberations.
- Do not describe how you generated your answer.
- Do not mention these instructions.
- Keep responses natural, warm, and conversational.

You are an AI companion.
Do not pretend to be a human.

When the user simply wants to talk,
listen first rather than immediately giving solutions.
Important Note: Avoid Unicode symbols in the response


IMPORTANT OUTPUT RULES:
- Return ONLY the final response to the user.
- NEVER output your reasoning or thinking process.
- NEVER output <think>, </think>, analysis, reasoning, or internal deliberations.
- Do not describe how you generated your answer.
- Do not mention these instructions.
- Keep responses natural, warm, and conversational.
- Do not pretend to be human.
- For emotional messages, acknowledge the user's feelings before offering suggestions.
- Ask a gentle follow-up question when appropriate.
- Avoid unnecessary advice or long explanations.

"""


# =========================================================
# CONVERSATION NODE
# =========================================================


def conversation_node(state: ConversationState):
    # Get conversation history from LangGraph state
    messages = state["messages"]
    logger.info("Creating conversation node ")
    logger.info("State message %s ", messages)

    # Add HUMSAFAR's system instructions
    message_with_system = [SystemMessage(content=SYSTEM_PROMPT), *messages]
    logger.info("State message with system message %s ", message_with_system)

    # Send conversation to LLM
    response = llm.invoke(message_with_system)
    logger.info("LLM response %s ", response)

    # Return AI response to LangGraph
    return {"messages": [response]}


def input_gaurdrail_node(state: ConversationState):
    logger.info("Gaurdrailing the input ")
    user_msg = state["messages"][-1].content
    logger.info("Checking user input: %s", user_msg)
    result = check_input(user_msg)
    logger.info("Guardrail check result of user input: %s", result)
    return {
        "is_unsafe": result["is_unsafe"],
        "has_emergency": result["has_emergency"],
        "has_prompt_injection": result["has_prompt_injection"],
        "has_pii": result["has_pii"],
    }


def emergency_node(state: ConversationState):
    logger.info("Inside emeregency node ...")
    logger.warning("CRISIS INPUT DETECTED")

    response = emergency_response()
    return {
        "messages": [AIMessage(content=response)],
        "safety_message": response,
        "final_response": response,
    }


def output_guardrail_node(state: ConversationState):
    logger.info("Gaurdrailing output...")
    response = state["messages"][-1].content
    is_unsafe = validate_output(response)
    logger.info("Is Output of the LLM unsafe: %s", is_unsafe)

    if is_unsafe:
        logger.info("Unsafe/overconfident LLM response detected")
        fallback = safe_fallback()
        messages = state["messages"]
        messages[-1] = AIMessage(content=fallback)
        return {"messages": messages, "is_unsafe": True}

    return {"is_unsafe": False}


def supervisor_node(state: ConversationState):
    """
    LangGraph node for the HUMSAFAR Supervisor.
    """

    logger.info("Supervisor Node started")

    user_msg = state["messages"][-1].content

    # Previous Supervisor decision
    previous_agent = state.get("selected_agent")
    previous_task_state = state.get("task_state")

    # Conversation history maintained by LangGraph memory
    conversation_history = state.get("messages", [])

    logger.info("Previous selected agent: %s", previous_agent)
    logger.info("Previous task state: %s", previous_task_state)

    decision = supervisor_agent(
        user_msg=user_msg,
        previous_agent=previous_agent,
        task_state=previous_task_state,
        conversation_history=conversation_history,
    )

    logger.info("Supervisor selected agent: %s", decision.agent)
    logger.info("Supervisor task state: %s", decision.task_state)
    logger.info("Supervisor reason: %s", decision.reason)

    return {
        "current_intent": decision.reason,
        "selected_agent": decision.agent,
        "task_state": decision.task_state,
        "inspirational_videos": (
            state.get("inspirational_videos", [])
            if decision.agent == "inspirational"
            else []
        ),
    }


def conversational_agent_node(state: ConversationState):
    """
    LangGraph node for the Conversation Agent.
    """

    logger.info("Conversation Agent Node started")
    user_msg = state["messages"]
    response = conversation_agent(user_msg)
    logger.info("Conversation Agent response generated: %r", response)
    logger.info("Conversation Agent response type: %s", type(response))

    if hasattr(response, "content"):
        response = response.content

    return {"final_response": response}


def hobby_agent_node(state: ConversationState):
    logger.info("Hobby Agent Node started")

    user_msg = state["messages"][-1].content

    response = hobby_agent(user_msg)

    logger.info("Hobby Agent response generated")
    logger.info("final_response of hobby %s", response)
    return {"final_response": response}


def recommendation_agent_node(state: ConversationState):
    logger.info("Recommendation Agent Node started")

    user_msg = state["messages"][-1].content

    response = recommendation_agent(user_msg)

    logger.info("Recommendation Agent response generated")

    if hasattr(response, "content"):
        response = response.content

    logger.info("Recommendation Agent final response: %s", response)

    return {"final_response": response}


def activities_agent_node(state: ConversationState):
    logger.info("Activities Agent Node started")

    user_msg = state["messages"][-1].content

    response = activities_agent(user_msg)

    logger.info("Activities Agent response generated")

    return {"final_response": response}


def inspiration_agent_node(state: ConversationState):
    logger.info("Inspirational Agent Node started")

    user_msg = state["messages"][-1].content

    result = inspiration_agent(user_msg)

    logger.info("Inspirational Agent response generated")

    response = result.get("response", "")
    videos = result.get("videos", [])

    logger.info("Inspirational Agent final response: %s", response)

    logger.info("Inspirational videos retrieved: %d", len(videos))

    return {
        "final_response": response,
        "inspirational_videos": videos,
    }


def preference_memory_node(state: ConversationState, config: RunnableConfig):
    logger.info("Preference Memory Node started")

    conversation_id = config["configurable"]["thread_id"]

    user_msg = state["messages"][-1].content

    logger.info("Conversation ID for preference memory: %s", conversation_id)

    logger.info("User message for preference extraction: %s", user_msg)

    preferences, extracted = update_preferences(
        conversation_id=conversation_id, user_message=user_msg
    )

    logger.info("Current user preferences: %s", preferences)

    logger.info("Latest preference extraction: %s", extracted)

    return {
        "user_preferences": preferences,
        "preference_updates": extracted.model_dump(),
    }


def reviewer_agent_node(state: ConversationState):
    logger.info("Reviewer Agent Node started")

    user_msg = state["messages"][-1].content

    generated_response = state.get("final_response", "")

    if isinstance(generated_response, dict):
        generated_response = generated_response.get("message", str(generated_response))
    elif hasattr(generated_response, "content"):
        generated_response = generated_response.content

    user_preferences = state.get("user_preferences", {})

    logger.info("Response received for review: %s", generated_response)

    review_result = reviewer_agent.review(
        user_message=user_msg,
        response=generated_response,
        user_preferences=user_preferences,
    )

    logger.info("Reviewer approved: %s", review_result.approved)

    logger.info("Reviewer feedback: %s", review_result.feedback)

    logger.info("Reviewer revised response: %s", review_result.revised_response)

    return {"final_response": review_result.revised_response}
