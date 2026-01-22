from botengine_pytest import BotEnginePyTest
from locations.location import Location


def test_lesson14_weather_publishes_state(monkeypatch):
    botengine = BotEnginePyTest({"time": 1685602800000, "trigger": 1, "locationId": 0})
    botengine.reset()

    # Provide fake weather APIs (BotEnginePyTest does not implement them by default).
    def fake_current(location_id, units=None):
        assert location_id == 0
        return {"resultCode": 0, "tempC": 21, "condition": "Clear", "units": units}

    def fake_forecast(location_id, units=None, hours=12):
        assert location_id == 0
        return {
            "resultCode": 0,
            "hours": hours,
            "units": units,
            "forecast": [{"hour": 1, "tempC": 20}, {"hour": 2, "tempC": 19}],
        }

    monkeypatch.setattr(
        botengine, "get_current_weather_by_location", fake_current, raising=False
    )
    monkeypatch.setattr(
        botengine, "get_weather_forecast_by_location", fake_forecast, raising=False
    )

    location = Location(botengine, 0)
    location.new_version(botengine)
    location.initialize(botengine)

    ms_key = "intelligence.lesson14.location_weather_microservice"
    mut = location.intelligence_modules[ms_key]

    mut.schedule_fired(botengine, "DAILY")

    state = botengine.get_state("lesson14/weather")
    assert state is not None
    assert state["scheduleId"] == "DAILY"
    assert state["current"]["tempC"] == 21
    assert state["forecast"]["hours"] == 12

