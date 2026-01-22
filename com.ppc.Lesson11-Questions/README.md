# Lesson 11: Asking Questions

This lesson shows how a bot can ask a question, receive an answer later, and persist that answer as configuration.

Questions enable a bot to ask users questions through UI's, define how the question gets rendered, and more. Think about your favorite survey tool - bots are armed with the same powerful set of tools, limited only by the UI capabilities.

## What you’ll build

- A location microservice (`intelligence/lesson11/location_questions_microservice.py`) that:
  - Asks a Boolean question using `botengine.generate_question(...)` + `botengine.ask_question(...)`
  - Handles `question_answered(...)`
  - Saves the answer into:
    - A location property (`lesson11_enable_questions`)
    - A UI-facing state variable (`lesson11/questions`)

## Run locally (recommended)

Use the repo’s microservice test runner:

```bash
botlab-tests --bundle com.ppc.Lesson11-Questions --directory tests
```

## Key files

- `com.ppc.Lesson11-Questions/intelligence/lesson11/index.py`
- `com.ppc.Lesson11-Questions/intelligence/lesson11/location_questions_microservice.py`
- `com.ppc.Lesson11-Questions/tests/test_lesson11_questions.py`
