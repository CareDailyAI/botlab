# Lesson 12 : Tagging People, Places, and Things

The botengine contains methods to tag and delete tags for people, places, and things. These tags can help segment users and proactively identify problems.

## What you’ll build

- A location microservice (`intelligence/lesson12/location_tags_microservice.py`) that:
  - Tags a user and location
  - Optionally tags a device if one exists
  - Publishes a summary to a UI-facing state variable at `lesson12/tags`
  - Demonstrates deleting the same tags

## Run locally (recommended)

```bash
botlab-tests --bundle com.ppc.Lesson12-Tags --directory tests
```

## Key files

- `com.ppc.Lesson12-Tags/intelligence/lesson12/index.py`
- `com.ppc.Lesson12-Tags/intelligence/lesson12/location_tags_microservice.py`
- `com.ppc.Lesson12-Tags/tests/test_lesson12_tags.py`