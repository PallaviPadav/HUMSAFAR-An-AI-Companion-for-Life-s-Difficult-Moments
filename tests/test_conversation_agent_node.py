from langchain_core.messages import HumanMessage

from graph.node import conversational_agent_node
from graph.state import ConversationState


def test_conversation_agent_node():
    state = ConversationState(
        messages=[HumanMessage(content="I have been feeling lonely lately.")],
        is_unsafe=False,
        has_emergency=False,
        has_prompt_injection=False,
        has_pii=False,
        safety_message="",
        current_intent=None,
        selected_agent=None,
        final_response=None,
    )

    result = conversational_agent_node(state)

    print("\nNode Result:")
    print(result)

    assert "messages" in result
    assert len(result["messages"]) == 1
    assert result["messages"][0].content
