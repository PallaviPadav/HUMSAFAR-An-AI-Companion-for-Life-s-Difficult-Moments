from schemas.agent_schema import AgentDecision


def test_agent_decision():
    decision = AgentDecision(
        agent="hobby", reason="The user wants to talk about their hobbies."
    )
    assert decision.agent == "hobby"
    assert decision.reason == "The user wants to talk about their hobbies."


def test_agent_decision_invalid():
    try:
        AgentDecision(agent="  ", reason="Invalid")
        assert False, "Invalid agent should have failed validation"
    except Exception:
        assert True
