from botengine_pytest import BotEnginePyTest
from locations.location import Location


def test_lesson19_publishes_behaviors_datastream_message(monkeypatch):
    botengine = BotEnginePyTest({})
    botengine.reset()

    # Behaviors should be delivered externally in this demo; allow it for pytest.
    monkeypatch.setattr(botengine, "is_test_location", lambda: False, raising=False)

    location = Location(botengine, 0)
    location.new_version(botengine)
    location.initialize(botengine)

    # UI-facing state is set
    state = botengine.get_state("lesson19/behaviors")
    assert state is not None
    assert state["deviceTypes"] == [9138]

    # External datastream message was sent
    msgs = botengine.get_datastream_messages()
    assert any(m["address"] == "set_behaviors" for m in msgs)

