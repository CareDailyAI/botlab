# Lesson 15 : Analytics

The `signals.analytics` module in `com.ppc.Bot` can be replaced with an implementation that allows developers to capture analytics to their favorite online analytics services. The core repo includes examples (Mixpanel, Amplitude).

This lesson shows a simple pattern:
- Use `signals.analytics.track(...)` to record events (and optionally create narratives).
- Use `Location.set_location_property(..., track=True)` to propagate “people” properties via analytics signals.

## What you’ll build

- A location microservice (`intelligence/lesson15/location_analytics_microservice.py`) that:
  - emits `analytics_track` datastream messages
  - emits `analytics_people_set` messages via location properties
  - publishes a small summary to `lesson15/analytics`

## Run locally (recommended)

```bash
botlab-tests --bundle com.ppc.Lesson15-Analytics --directory tests
```
