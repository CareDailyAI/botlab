from botengine_pytest import BotEnginePyTest
from locations.location import Location


def test_lesson11_asks_question_and_persists_answer():
    botengine = BotEnginePyTest({})
    botengine.reset()

    location = Location(botengine, 0)
    location.new_version(botengine)
    location.initialize(botengine)

    ms_key = "intelligence.lesson11.location_questions_microservice"
    mut = location.intelligence_modules[ms_key]

    # The question should have been asked during initialize(); flush it into the test question store.
    botengine.flush_questions()

    q = botengine.retrieve_question("lesson11.enable_questions")
    assert q is not None
    assert q.answer_status == BotEnginePyTest.ANSWER_STATUS_QUEUED

    # Simulate an answer arriving on a question trigger.
    q.answer = True
    q.answer_status = BotEnginePyTest.ANSWER_STATUS_ANSWERED
    mut.question_answered(botengine, q)

    # Location property is the canonical persisted configuration for other microservices.
    assert (
        location.get_location_property(botengine, "lesson11_enable_questions") is True
    )

    # State variable is UI-facing content.
    state = botengine.get_state("lesson11/questions")
    assert state is not None
    assert state["answered"] is True
    assert state["answer"] is True

