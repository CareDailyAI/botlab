# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

BotLab is a Python-based microservices framework for building IoT bot services that run 24/7 in the cloud. Bots analyze real-time and historical data from internet-connected devices to add intelligent features and services.

## Commands

### Installation
```bash
pip install .                    # Install the package
pip install ".[dev]"             # Install with dev dependencies (pytest, requests_mock)
```

### Running a Bot (Playback Mode)
```bash
botlab --playback tests/data/14-days-of-data -r com.ppc.Lesson1-Microservices
```

### Running Tests
```bash
pytest                           # Run all tests in tests/ directory
pytest tests/test_botengine.py   # Run specific test file
```

For bot microservice testing (i.e., tests that require a merged bot runtime environment), use `botlab-tests`.

```bash
botlab-tests                                # Run tests in default bundle (com.ppc.Tests)
botlab-tests --bundle com.ppc.Bot           # Run tests within a specific bot bundle
botlab-tests --directory tests              # Only run the bot's tests/ directory

# Filter down to microservice-related tests (passes through to pytest via `-k`)
botlab-tests --mut meta_analysis
botlab-tests --mut meta_analysis --mut occupancy_analysis

# Run a specific test file (auto-searches microservice tests when used with --mut)
botlab-tests --mut meta_analysis --test-file test_missedbathroom.py
botlab-tests --mut meta_analysis --test-file test_missedbathroom.py::test_function

# Use a different BOTLAB core checkout as the merge source
botlab-tests --core ../botlab-private

# Preload variables / location context for regression-style tests
botlab-tests --variables data.variable --location_id 123

# Verbose pytest output
botlab-tests --verbose
```

### Linting
```bash
ruff check .                     # Check code style (configured in pyproject.toml)
ruff format .                    # Format code
```

## Architecture

### Bot Structure
Bots follow an inheritance model using `structure.json`:
- `com.ppc.Bot` is the foundational bot framework (never edit directly)
- Custom bots extend `com.ppc.Bot` via the `extends` field in `structure.json`
- When generating/committing, files from the parent bot are copied first, then child bot files overlay them

### Core Components

**Entry Point**: `com.ppc.Bot/bot.py`
- `run(botengine)` is the main entry point
- Loads the `Controller`, synchronizes devices, triggers events

**Controller** (`com.ppc.Bot/controller.py`):
- Coordinates all locations and devices
- Manages `Location` objects keyed by location ID

**Location** (`com.ppc.Bot/locations/location.py`):
- Represents a physical location (e.g., home)
- Contains devices, intelligence modules, and filters
- Tracks security state, occupancy status, mode (HOME/AWAY/STAY/TEST)

**Device** (`com.ppc.Bot/devices/device.py`):
- Base class for all device types
- Device-specific implementations in `devices/` subdirectories (alarm, button, camera, entry, motion, etc.)

### Microservices Architecture

**Intelligence Modules** (`com.ppc.Bot/intelligence/intelligence.py`):
- Event-driven services extending the `Intelligence` base class
- Two types:
  - **Location microservices**: Coordinate multiple devices across a location
  - **Device microservices**: Add features to specific device types

**index.py Pattern**:
- Each bot/package contains an `index.py` that registers microservices
- `MICROSERVICES` dict maps device types to device microservices
- `LOCATION_MICROSERVICES` list registers location-wide services

**Signals** (`com.ppc.Bot/signals/`):
- Inter-microservice communication via internal data stream messages
- One-way communication pattern using signal interface files

**Filters** (`com.ppc.Bot/filters/filter.py`):
- Data filtration layer that can modify device measurements before reaching microservices
- Useful for data correction/normalization

### Event Flow
1. Bot triggered by device data, timers, schedules, etc.
2. `bot.run()` loads Controller from memory
3. Controller synchronizes devices and locations
4. `new_version()` called if bot version changed
5. `initialize()` called on every execution
6. Event-specific methods called on microservices (e.g., `device_measurements_updated()`, `timer_fired()`)

### Key Files

- `structure.json`: Bot composition (extends, pip dependencies, microservice paths)
- `runtime.json`: Trigger types, schedules, device subscriptions
- `index.py`: Microservice registration
- `properties.py`: Bot properties and configuration

### BotEngine API

Located in `src/botengine/botengine.py`:
- Provides the interface to cloud services
- Handles device commands, timers, data requests, notifications
- Passed as first argument to all microservice methods

### Time Utilities

Constants in `com.ppc.Bot/utilities/utilities.py`:
- `ONE_SECOND_MS`, `ONE_MINUTE_MS`, `ONE_HOUR_MS`, `ONE_DAY_MS`, `ONE_WEEK_MS`
- Mode constants: `MODE_HOME`, `MODE_AWAY`, `MODE_STAY`, `MODE_TEST`
- Occupancy states: `OCCUPANCY_STATUS_PRESENT`, `OCCUPANCY_STATUS_ABSENT`, etc.

## Creating a New Bot

1. Create a new directory `com.yourcompany.YourBot/`
2. Add `structure.json` with `"extends": "com.ppc.Bot"`
3. Create `intelligence/` directory with microservices
4. Add `index.py` to register microservices
5. Optionally add `runtime.json` for triggers and schedules

## Testing

Tests are in `tests/` directory. The `pytest.ini` excludes `com.ppc.*` and hidden directories from test collection. Use `requests_mock` for API mocking.
