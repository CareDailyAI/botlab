"""
Lesson 14 - Weather

Demonstrates how a location microservice can retrieve weather information using BotEngine APIs
and publish a small summary into a state variable for UI consumption.
"""

from intelligence.intelligence import Intelligence  # type: ignore


STATE_ADDRESS = "lesson14/weather"


class LocationWeatherMicroservice(Intelligence):
    def __init__(self, botengine, parent):
        super().__init__(botengine, parent)

    def schedule_fired(self, botengine, schedule_id):
        self._update_weather(botengine, schedule_id=schedule_id)

    def initialize(self, botengine):
        # Keep initialize lightweight; only refresh on schedule triggers in real usage.
        return

    def _update_weather(self, botengine, schedule_id=None):
        # Prefer location-based API.
        weather_json = None
        forecast_json = None

        if hasattr(botengine, "get_current_weather_by_location"):
            try:
                weather_json = botengine.get_current_weather_by_location(
                    botengine.get_location_id(), units="m"
                )
            except Exception:
                weather_json = None

        if hasattr(botengine, "get_weather_forecast_by_location"):
            try:
                forecast_json = botengine.get_weather_forecast_by_location(
                    botengine.get_location_id(), units="m", hours=12
                )
            except Exception:
                forecast_json = None

        botengine.set_state(
            STATE_ADDRESS,
            {
                "scheduleId": schedule_id,
                "current": weather_json,
                "forecast": forecast_json,
            },
            overwrite=True,
        )

