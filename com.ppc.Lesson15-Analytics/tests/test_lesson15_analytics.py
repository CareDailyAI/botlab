from botengine_pytest import BotEnginePyTest
from locations.location import Location


def test_lesson15_analytics_emits_datastream_messages(monkeypatch):
    botengine = BotEnginePyTest({})
    botengine.reset()

    # Allow analytics signals to emit datastream messages (they are disabled on test locations).
    monkeypatch.setattr(botengine, "is_test_location", lambda: False, raising=False)

    location = Location(botengine, 0)
    location.new_version(botengine)
    location.initialize(botengine)

    # Verify UI-facing state content
    state = botengine.get_state("lesson15/analytics")
    assert state is not None
    assert state["event"] == "lesson15.analytics_demo"

    # Verify internal signal handlers were invoked (signals -> internal datastream delivery)
    assert state["lastAnalyticsTrack"] is not None
    assert state["lastAnalyticsTrack"]["event_name"] == "lesson15.analytics_demo"
    assert state["lastAnalyticsPeopleSet"] is not None
    assert (
        state["lastAnalyticsPeopleSet"]["properties_dict"]["lesson15_demo_property"]
        == "enabled"
    )

