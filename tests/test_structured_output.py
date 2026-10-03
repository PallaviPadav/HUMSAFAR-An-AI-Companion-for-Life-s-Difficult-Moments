from graph.structured_output import structured_llm
from schemas.agent_schema import AgentDecision


def test_structured_agent_decision():
    user_message = """
    I used to love smoking, but I haven't smoked in a long time.
    I think I would like to start smoking again.
    """

    decision = structured_llm.invoke(user_message)

    assert isinstance(decision, AgentDecision)
    print(decision)
    print(isinstance(decision, AgentDecision))

    assert decision.agent in [
        "conversation",
        "hobby",
        "activity",
        "inspiration",
        "recommendation",
    ]
    print(
        decision.agent
        in [
            "conversation",
            "hobby",
            "activity",
            "inspiration",
            "recommendation",
        ]
    )
    assert isinstance(decision.reason, str)
    print(isinstance(decision.reason, str))
    assert len(decision.reason) > 0
