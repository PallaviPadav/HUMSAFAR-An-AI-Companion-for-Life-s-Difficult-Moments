from graph.workflow import graph


def test_conversation_supervisor_graph():
    config = {"configurable": {"thread_id": "test-conversation-001"}}

    result = graph.invoke(
        {
            "messages": [
                {"role": "user", "content": "I have been feeling lonely lately."}
            ],
            "is_unsafe": False,
            "has_emergency": False,
            "has_prompt_injection": False,
            "has_pii": False,
            "safety_message": "",
            "current_intent": None,
            "selected_agent": None,
            "final_response": None,
        },
        config=config,
    )

    print("\nFinal Graph State:")
    print(result)

    print("\nSelected Agent:")
    print(result["selected_agent"])

    print("\nFinal Message:")
    print(result["messages"][-1].content)

    assert result["selected_agent"] == "conversation"
    assert result["messages"][-1].content
