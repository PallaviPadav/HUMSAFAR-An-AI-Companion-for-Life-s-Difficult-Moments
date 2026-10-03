from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from graph.state import ConversationState

# from graph.node import conversation_node
from utils.logger import get_logger
from graph.node import (
    input_gaurdrail_node,
    emergency_node,
    conversational_agent_node,
    supervisor_node,
    output_guardrail_node,
    hobby_agent_node,
    activities_agent_node,
    recommendation_agent_node,
    inspiration_agent_node,
)


logger = get_logger(__name__)
logger.info("Creating State Graph")
builder = StateGraph(ConversationState)

builder.add_node("input_gaurdrail", input_gaurdrail_node)
# builder.add_node("conversation", conversation_node)
builder.add_node("emergency_gaurdrail", emergency_node)
builder.add_node("conversational_agent_node", conversational_agent_node)
builder.add_node("supervisor_node", supervisor_node)
builder.add_node("output_guardrail", output_guardrail_node)
builder.add_node("hobby_agent_node", hobby_agent_node)
builder.add_node("activities_agent_node", activities_agent_node)
builder.add_node("recommendation_agent_node", recommendation_agent_node)
builder.add_node("inspiration_agent_node", inspiration_agent_node)


def route_after_supervisor(state: ConversationState):
    """
    Route the conversation to the appropriate specialist agent.
    """
    logger.info("State: %s", state)
    selected_agent = state.get("selected_agent")
    logger.info("Routing to selected agent: %s", selected_agent)

    return selected_agent


def route_after_input(state: ConversationState):
    logger.info(state)
    if state.get("has_emergency", False):
        logger.info("Before routing check for emergency: emergency is present")
        return "emergency"
    logger.info("No emergency route to supervisor node")
    return "supervisor_node"


builder.add_edge(START, "input_gaurdrail")
builder.add_conditional_edges(
    "input_gaurdrail",
    route_after_input,
    {"emergency": "emergency_gaurdrail", "supervisor_node": "supervisor_node"},
)
builder.add_conditional_edges(
    "supervisor_node",
    route_after_supervisor,
    {
        "conversation": "conversational_agent_node",
        "hobby": "hobby_agent_node",
        "activities": "activities_agent_node",
        "recommendation": "recommendation_agent_node",
        "inspirational": "inspiration_agent_node",
    },
)
builder.add_edge("conversational_agent_node", "output_guardrail")
builder.add_edge("hobby_agent_node", "output_guardrail")
builder.add_edge("activities_agent_node", "output_guardrail")
builder.add_edge("recommendation_agent_node", "output_guardrail")
builder.add_edge("inspiration_agent_node", "output_guardrail")
builder.add_edge("output_guardrail", END)
builder.add_edge("emergency_gaurdrail", END)

# checkpointer = SqliteSaver.from_conn_string("data/humsafar_memory.db")
checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)
logger.info("Completed State Graph")
