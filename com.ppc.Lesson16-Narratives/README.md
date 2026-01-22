# Lesson 16 : Narratives

Narratives allow a bot to articulate, in human language, what is happening inside a home. This can allow an auditable trail of history which can be viewed by end users and deciphered by customer support to help diagnose problems and answer questions.

## What you’ll build

- A location microservice (`intelligence/lesson16/location_narratives_microservice.py`) that:
  - Creates a narrative (History entry)
  - Stores the narrative ID/time so it can later update the same record
  - Publishes a summary to `lesson16/narratives` via `botengine.set_state(...)`

## Key APIs

Please see the following methods in `com.ppc.Bot/locations/location.py`:

    location_object.narrate(self, botengine, title, description, priority, icon, timestamp_ms=None, file_ids=None, extra_json_dict=None, update_narrative_id=None, update_narrative_timestamp=None)
    location_object.delete_narration(self, botengine, narrative_id, narrative_timestamp)

## Run locally (recommended)

```bash
botlab-tests --bundle com.ppc.Lesson16-Narratives --directory tests
```
