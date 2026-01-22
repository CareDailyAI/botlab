# Lesson 21 : Edge Computing

You will need an edge-capable gateway in your possession to run bots on the edge.

## What you’ll build

- A location microservice (`intelligence/lesson21/location_edge_microservice.py`) that publishes an `edge` / `cloud` mode flag to `lesson21/edge`.
- The code demonstrates the pattern “**gate cloud-only work when running on edge**”.

## Run locally (recommended)

```bash
botlab-tests --bundle com.ppc.Lesson21-EdgeComputing --directory tests
```

