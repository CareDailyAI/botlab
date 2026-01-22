from botengine_pytest import BotEnginePyTest
from locations.location import Location


def test_lesson12_tags_and_deletes():
    botengine = BotEnginePyTest({})
    botengine.reset()

    location = Location(botengine, 0)
    location.new_version(botengine)
    location.initialize(botengine)

    ms_key = "intelligence.lesson12.location_tags_microservice"
    mut = location.intelligence_modules[ms_key]

    # Tags were created once
    assert any(t.get("tag") == "lesson12.user" for t in botengine.user_tags)
    assert any(t.get("tag") == "lesson12.location" for t in botengine.location_tags)

    # UI-facing state variable exists
    state = botengine.get_state("lesson12/tags")
    assert state is not None
    assert state["deleted"] is False

    # Now delete the tags
    mut.delete_demo_tags(botengine)

    assert "lesson12.user" in botengine.deleted_user_tags
    assert "lesson12.location" in botengine.deleted_location_tags

    state2 = botengine.get_state("lesson12/tags")
    assert state2 is not None
    assert state2["deleted"] is True

