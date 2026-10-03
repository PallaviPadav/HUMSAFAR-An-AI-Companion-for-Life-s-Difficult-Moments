from langchain_core.messages import HumanMessage

from agents.conversation_agent import conversation_agent


def test_conversation_agent():
    messages = [HumanMessage(content="I have been feeling lonely lately.")]

    response = conversation_agent(messages)

    print("\nConversation Agent Response:")
    print(response.content)

    assert response is not None
    assert response.content
    assert isinstance(response.content, str)


def test_conversation_agent_emotional_response():
    messages = [
        HumanMessage(
            content="I worked really hard for something, "
            "but things did not work out."
        )
    ]

    response = conversation_agent(messages)

    print("\nEmotional Response:")
    print(response.content)

    assert response.content
