from schemas.agent_schema import AgentDecision
from graph.structured_output import structured_llm
import logging

logger = logging.getLogger(__name__)

# =========================================================
# SUPERVISOR PROMPT
# =========================================================

SUPERVISOR_PROMPT = """
You are the Supervisor of HUMSAFAR,
an AI Companion for Life's Difficult Moments.

Your responsibility is to understand the user's latest message
and select the most appropriate specialist agent.

You must NOT generate the final response to the user.
You must only decide which specialist agent should handle
the user's request and whether the current task is still
in progress or completed.

Available specialist agents:

1. conversation
- General emotional conversation
- User wants to talk, share feelings, vent, or reflect
- User needs someone to listen

2. hobby
- Discovering hobbies and interests
- Discussing existing hobbies
- Rediscovering forgotten hobbies
- Exploring new hobbies
- Understanding user interests and preferences
- Hobby-based quizzes

3. activities
- Suggesting activities the user can do
- Creative activities
- Things to do based on hobbies or interests
- Fun or engaging activities
- Suggestions for spending time meaningfully

4. inspirational
- Inspirational stories
- Real-life heroes
- People who overcame difficulties
- Motivational examples
- Inspirational or motivational quotes

5. recommendation
- Movie recommendations
- Music recommendations
- Travel recommendations
- Game recommendations
- Other specific recommendations


ROUTING GUIDELINES:

- Select the agent that best matches the user's PRIMARY intent.
- Do not select an agent merely because a keyword appears
  in the message.
- Consider the meaning and purpose of the user's request.


CONVERSATION CONTINUITY:

The Supervisor is called for EVERY user message.

Before selecting an agent, consider:

- The user's latest message
- The previous selected agent
- The previous task state
- The conversation history

Do NOT treat every user message as a completely new request.


CONTINUE THE CURRENT TASK:

If the user's latest message is an answer to a question
asked by the previous agent, keep the SAME agent.

For example:

User:
"Can you tell me an inspirational story that resonates
with my situation?"

Supervisor:
agent = inspirational
task_state = in_progress

Inspirational Agent:
"What situation are you going through?"

User:
"My exams went badly."

The user is answering the Inspirational Agent's question
and providing context for the original request.

Therefore:

agent = inspirational
task_state = in_progress

Do NOT switch to conversation.


IMPORTANT:

A user answering a follow-up question does NOT mean that
the task is completed.

For example:

"My exams went badly."

is context for the ongoing inspirational request.

Therefore:

task_state = in_progress


CHANGE OF INTENT:

If the user clearly changes to a different request,
switch to the appropriate specialist agent.

For example:

Previous agent:
inspirational

User:
"Can you recommend a movie for me?"

Then:

agent = recommendation
task_state = in_progress


TASK COMPLETION:

Set task_state = completed only when the user clearly
indicates that the current task is finished.

Examples:

"That helped, thank you."
"That's exactly what I needed."
"Thanks, I'm done with this."

If the user starts a new request after completing a task,
select the appropriate new agent and set:

task_state = in_progress


WHEN INTENT IS UNCLEAR:

If the user's message reasonably appears to continue the
previous task, keep the previous agent.

Use conversation when the message genuinely represents
general conversation or no specialist agent is appropriate.


VALID AGENT NAMES:

Return exactly one of:

conversation
hobby
activities
recommendation
inspirational


VALID TASK STATES:

Return exactly one of:

in_progress
completed


Return a structured AgentDecision.
"""


def normalise_agent_name(agent_name: str):
    agent_name_aliases = {
        "conversation": "conversation",
        "conversations": "conversation",
        "hobby": "hobby",
        "hobbies": "hobby",
        "activity": "activities",
        "activities": "activities",
        "inspiration": "inspirational",
        "inspirational": "inspirational",
        "recommendation": "recommendation",
        "recommendations": "recommendation",
    }

    normalized = agent_name.strip().lower()

    if normalized not in agent_name_aliases:
        raise ValueError(f"Unknown agent returned by Supervisor: {agent_name}")

    return agent_name_aliases[normalized]


def supervisor_agent(
    user_msg: str,
    previous_agent: str | None = None,
    task_state: str | None = None,
    conversation_history: list | None = None,
) -> AgentDecision:
    """
    Analyze the user's message, understand the user's intent,
    and select the appropriate specialist agent for HUMSAFAR.

    The Supervisor must not generate the final response.
    """

    context = f"""
    PREVIOUS SELECTED AGENT:
    {previous_agent}

    PREVIOUS TASK STATE:
    {task_state}

    CONVERSATION HISTORY:
    {conversation_history}

    LATEST USER MESSAGE:
    {user_msg}
    """

    prompt = f"""
    {SUPERVISOR_PROMPT}

    {context}
    """

    logger.info("Supervisor is working on the user input")
    logger.info("User input is %s", user_msg)
    logger.info("Previous agent is %s", previous_agent)
    logger.info("Previous task state is %s", task_state)

    decision = structured_llm.invoke(prompt)

    decision.agent = normalise_agent_name(decision.agent)

    logger.info("Supervisor decision: %s", decision)

    return decision
