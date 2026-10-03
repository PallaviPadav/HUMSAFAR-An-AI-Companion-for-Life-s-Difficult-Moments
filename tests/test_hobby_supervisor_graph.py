from graph.workflow import graph


def test_hobby_supervisor_graph():
    config = {"configurable": {"thread_id": "test-hobby-001"}}

    result = graph.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "I feel lonely and I think I need "
                        "a hobby to keep myself engaged."
                    ),
                }
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

    print("\nFINAL RESULT:")
    print(result)

    assert result["selected_agent"] == "hobby"
    assert result["final_response"] is not None
    assert len(result["final_response"]) > 0
