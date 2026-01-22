# Lesson 20 : Rules

Rules enable users to create their own "if-this-then-than" statements. Bot developers can create new rule phrases for devices.

## What you’ll build

- A location microservice (`intelligence/lesson20/location_rules_microservice.py`) that:
  - calls `botengine.get_rules(...)`
  - demonstrates toggling rules with `botengine.toggle_all_rules(...)`
  - publishes a summary to `lesson20/rules`

## Run locally (recommended)

```bash
botlab-tests --bundle com.ppc.Lesson20-Rules --directory tests
```
