from botengine_pytest import BotEnginePyTest
from locations.location import Location


def test_lesson20_reads_and_toggles_rules(monkeypatch):
    botengine = BotEnginePyTest({})
    botengine.reset()

    fake_rules = {"rules": [{"id": 1, "enabled": True}]}
    monkeypatch.setattr(botengine, "get_rules", lambda device_id=None: fake_rules, raising=False)
    monkeypatch.setattr(botengine, "toggle_all_rules", lambda enable, **kwargs: ["ok"], raising=False)

    location = Location(botengine, 0)
    location.new_version(botengine)
    location.initialize(botengine)

    # initialize() should refresh rules into state
    state = botengine.get_state("lesson20/rules")
    assert state is not None
    assert state["rules"] == fake_rules

    # Toggle all rules
    ms_key = "intelligence.lesson20.location_rules_microservice"
    mut = location.intelligence_modules[ms_key]
    mut.toggle_all(botengine, enable=False)

    state2 = botengine.get_state("lesson20/rules")
    assert state2["toggled"] is True
    assert state2["enable"] is False

