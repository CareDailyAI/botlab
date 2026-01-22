from botengine_pytest import BotEnginePyTest
from locations.location import Location


def test_lesson18_publishes_user_snapshot():
    botengine = BotEnginePyTest({})
    botengine.reset()

    location = Location(botengine, 0)
    location.new_version(botengine)
    location.initialize(botengine)

    state = botengine.get_state("lesson18/users")
    assert state is not None
    assert state["count"] >= 1
    assert state["users"][0]["id"] is not None

