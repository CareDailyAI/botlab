# Lesson 18 : User Management

Bots can identify users that are associated with a location, and get triggered when a user gets added or removed.

## What you’ll build

- A location microservice (`intelligence/lesson18/location_user_management_microservice.py`) that calls `botengine.get_location_users()` and publishes a summarized list to `lesson18/users`.

## Run locally (recommended)

```bash
botlab-tests --bundle com.ppc.Lesson18-UserManagement --directory tests
```