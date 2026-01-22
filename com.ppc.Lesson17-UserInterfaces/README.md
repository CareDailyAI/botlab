# Lesson 17 : Delivering content from bots to UIs

Bots can save some addressable state information in the form of raw JSON content which apps and UI's can retrieve. 

To leverage this, use `botengine.set_state(...)` (or `Location` helper methods that call it).

## What you’ll build

- A location microservice (`intelligence/lesson17/location_ui_state_microservice.py`) that publishes a payload to `lesson17/ui`.
- A datastream listener (`lesson17_ui_state`) so apps can push data into the bot and have the bot update the UI state in response.

## Key API

The `BotEngine` method:

    botengine.set_state(address, json_content, overwrite=True, ...)

## App → Bot interaction via Data Stream messages

Bots can also **receive** data stream messages at named addresses. This is a simple way for an app (or another bot) to send data into a bot microservice and trigger UI updates.

### 1) Declare the datastream address in `runtime.json`

In `intelligence/lesson17/runtime.json`, add the address to `dataStreams`:

```json
{
  "version": {
    "dataStreams": [
      { "address": "lesson17_ui_state" }
    ]
  }
}
```

This tells the platform that your bot can receive messages at this address.

### 2) Handle the message in your microservice

When the bot receives a message, the microservice base class (`Intelligence`) routes it like this:

- If the microservice has a method whose name matches the datastream address, it will be invoked.

So for address `lesson17_ui_state`, implement:

- `def lesson17_ui_state(self, botengine, content): ...`

In this lesson, that handler writes the incoming content into the UI-facing state at `lesson17/ui`:

- the app sends some JSON payload to `lesson17_ui_state`
- the bot stores it under `lesson17/ui` so the UI can render it

### 3) Suggested message shape

Use a stable, versioned envelope so the UI and bot can evolve safely:

```json
{
  "type": "ui_interaction",
  "version": 1,
  "action": "set",
  "payload": {
    "example": "hello from the app"
  }
}
```

### 4) State address vs datastream address

- **Datastream address** (`lesson17_ui_state`): how an app *pushes* a message into the bot.
- **State address** (`lesson17/ui`): how a UI *pulls* the latest computed content from the bot.

## Run locally (recommended)

```bash
botlab-tests --bundle com.ppc.Lesson17-UserInterfaces --directory tests
```

This allows bots to generate reports and deliver "bot-only" information directly into native user interfaces.

## Notes for UI developers

- The UI must know the state `address` to pull data from.
- Bot + UI teams should agree in advance on the address and JSON schema.