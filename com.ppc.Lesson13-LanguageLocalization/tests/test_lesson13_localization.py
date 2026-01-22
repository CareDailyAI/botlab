from botengine_pytest import BotEnginePyTest
from locations.location import Location


def test_lesson13_localization_state():
    botengine = BotEnginePyTest({})
    botengine.reset()

    location = Location(botengine, 0)
    location.new_version(botengine)
    location.initialize(botengine)

    state = botengine.get_state("lesson13/localization")
    assert state is not None
    assert "correct" in state
    assert state["correct"].startswith("Hello from ")
    assert state["wrongExampleKey"] == "Hello from BotLab"

