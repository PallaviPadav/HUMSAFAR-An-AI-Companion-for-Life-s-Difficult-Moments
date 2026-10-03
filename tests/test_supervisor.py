from graph.supervisor import supervisor_agent


def test_conversation_routing():
    decision = supervisor_agent(
        "I feel lonely and I just want someone to listen to me."
    )

    print(decision)

    assert decision.agent == "conversation"


def test_hobby_routing():
    decision = supervisor_agent(
        "I want to discover some hobbies. I used to enjoy painting."
    )

    print(decision)

    assert decision.agent == "hobby"


def test_hobby_quiz_routing():
    decision = supervisor_agent("Can you give me a fun hobby quiz?")

    print(decision)

    assert decision.agent == "hobby"


def test_activity_routing():
    decision = supervisor_agent("I want something creative to do today.")

    print(decision)

    assert decision.agent == "activity"


def test_inspiration_routing():
    decision = supervisor_agent("Tell me about someone who overcame difficult times.")

    print(decision)

    assert decision.agent == "inspiration"


def test_recommendation_routing():
    decision = supervisor_agent("Can you recommend a good movie for tonight?")

    print(decision)

    assert decision.agent == "recommendation"
