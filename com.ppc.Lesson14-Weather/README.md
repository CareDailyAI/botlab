# Lesson 14 : Weather

The botengine contains weather functions which can extract current weather and forecasted weather.

Weather API’s cost money and typically require a subscription service to leverage in a bot.

## What you’ll build

- A location microservice (`intelligence/lesson14/location_weather_microservice.py`) that calls:
  - `botengine.get_current_weather_by_location(...)`
  - `botengine.get_weather_forecast_by_location(...)`
- The microservice publishes the result to a UI-facing state variable at `lesson14/weather`.

## Run locally (recommended)

```bash
botlab-tests --bundle com.ppc.Lesson14-Weather --directory tests
```
