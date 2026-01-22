from botengine_pytest import BotEnginePyTest
from locations.location import Location


def test_lesson21_edge_flag_false_by_default():
    botengine = BotEnginePyTest({})
    botengine.reset()

    location = Location(botengine, 0)
    location.new_version(botengine)
    location.initialize(botengine)

    state = botengine.get_state("lesson21/edge")
    assert state is not None
    assert state["edge"] is False
    assert state["mode"] == "cloud"


def test_lesson21_edge_flag_true_when_set():
    botengine = BotEnginePyTest({})
    botengine.reset()
    botengine.edge = True  # simulate edge runtime

    location = Location(botengine, 0)
    location.new_version(botengine)
    location.initialize(botengine)

    state = botengine.get_state("lesson21/edge")
    assert state is not None
    assert state["edge"] is True
    assert state["mode"] == "edge"

