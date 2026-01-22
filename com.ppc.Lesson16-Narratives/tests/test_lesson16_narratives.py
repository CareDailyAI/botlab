from botengine_pytest import BotEnginePyTest
from locations.location import Location


def test_lesson16_creates_and_updates_narrative():
    botengine = BotEnginePyTest({"time": 1685602800000, "trigger": 1, "locationId": 0})
    botengine.reset()

    location = Location(botengine, 0)
    location.new_version(botengine)
    location.initialize(botengine)

    ms_key = "intelligence.lesson16.location_narratives_microservice"
    mut = location.intelligence_modules[ms_key]

    mut.create_or_update_demo_narrative(botengine, schedule_id="DAILY")
    state = botengine.get_state("lesson16/narratives")
    assert state is not None
    assert state["scheduleId"] == "DAILY"
    assert state["narrativeId"] is not None
    assert state["narrativeTime"] is not None

    # BotEnginePyTest stores narratives for later retrieval.
    stored = botengine.get_narration(state["narrativeId"], admin=False)
    assert stored is not None
    assert stored["title"] == "Lesson 16 demo narrative"

    # Update the same narrative ID by calling again
    prev_id = state["narrativeId"]
    mut.create_or_update_demo_narrative(botengine, schedule_id="DAILY")
    state2 = botengine.get_state("lesson16/narratives")
    # In BotEnginePyTest, update calls return a new mock narrative ID.
    assert state2["narrativeId"] != prev_id

