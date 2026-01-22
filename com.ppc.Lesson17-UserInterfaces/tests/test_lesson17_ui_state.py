from botengine_pytest import BotEnginePyTest
from locations.location import Location


def test_lesson17_publishes_ui_state_on_initialize():
    botengine = BotEnginePyTest({})
    botengine.reset()

    location = Location(botengine, 0)
    location.new_version(botengine)
    location.initialize(botengine)

    state = botengine.get_state("lesson17/ui")
    assert state is not None
    assert state["lesson"] == 17
    assert state["message"].startswith("Hello UI")

