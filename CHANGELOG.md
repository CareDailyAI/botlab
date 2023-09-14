All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [9.0.6] - 2023-08-23

### Fixed
- Use /espapi/version api when checking cloud server version
- Botengine playback should reference all miscroservice schedules
- location narrate method to include narrative_type param
- narrative type defines and use utilities class for them
- Refactor controller device class instantiation to allow class import from external modules
- Lambda and cloud logging and enabled info log level
- Error logging for question trigger exception
- Set default runtime timeout to 510 seconds
- Log error messages if the bot cannot start
- Wrap logger in try:except
- Removed json indents from logging
- Botengine pytest timer sorting
- Include utilities test class
- Missing botengine_pytest stubs
- AWS Secret Manager implementation requires urllib3 version 1
- Trigger logging
- Botengine playback logging and execution error
- Botengine_pytest timer/alarm are interchangeable
- Included logging to display ISO time during tests
- Amplitude analytics should post events at the time they are tracked, not the time the bot is executed (added tests too)
- Botengine pytest alarm/timer handling and update outdated class api
- Botengine playback to reference at least 1 resident to support conversations
- Location locale should default to "en"
- Utility class to include command console links to CareDailyInsights
- Bot playback log files
- Botengine playback inclusion of question objects
- BOT-1089 Data Request ML threading
- Error handling when loading controller.
- Cleanup app api references
- track_and_notify analytic narratives should be differentiated from all others
- pytest executable

### Changed
- Update bot output structure

### Added
- Execution statistics to location microservices and signals
- Cloudwatch Logging botengine cli command parsers and apis
- MMS botengine method parameters
- Sample app store links
- Added additional logging and ignore missing domain property CHAT_ASSISTANT_NAME
- Tests for bot.py class to more closely align with actual lambda executions
- Voice Call microservice and model
- OpenAI utility functions
- AWS Secret Manager class method to botengine
- Include botengine class tests
- French and Swedish locales
- Doxygen support
- Confidence state machine
- Alarm, Health, and Proxy devices
- Daily Report, Dashboard, Daylight, and Tasks single classes
- Example filter microservice
- SMS Delivery microservice
- Maestro CLI Tool

### Removed

## [8.2.0] - 2022-11-04

### Fixed
- Reduced some logging
- Data request need more time to wait to avoid the api request locked
- Include -b bundle_id parameter in pytest
- `--botinfo` check to get bot marketing information
- Do not attempt to purchase a committed bot if no location ID or organization ID is provided
- Use default device goal ID as defined by the bot if not set

### Changed
- Python runtime to 3.9
- Moved memory and runtime fields from PUT developer/version to PUT developer/upload
- Limit execution time
- Asynchronous data request (device historical data) when bot start up
- Queue up device measurement and intelligence modules for follow-on executions
- Asynchronous for url request when bot start up(bot variables)

### Added
- Method to check cloud versions from botengine cli
- CLI interface to update a bot version's runtime parameters (memory and timeout)
- Playback data to include triggers for schedules
- Support multiple schedules in one input
- Additional timeout to /analytics/start api
- Playback logged to specified session id
- ML Error logging for bot developers
- Push notification title, subtitle and category parameters
- tag_release cli command

[Unreleased]: https://github.com/caredailyai/botlab/compare/v9.0.6...HEAD
[9.0.6]: https://github.com/caredailyai/botlab/compare/v8.2.0...v9.0.6
[8.2.0]: https://github.com/caredailyai/botlab/tag/releases/v8.2.0