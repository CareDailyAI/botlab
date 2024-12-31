All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [9.6.0] - 2024-12-30

### Fixed

- Reduced warning from missing domain properties
- Organization User Notification email templates
- Vayyar radar fall test
- Reduce warnings for missing domain settings when gathering organization user notification categories
- Missing localized keys
- Device class extraction should be accessible by other services
- Rules engine device class extraction should be generalized
- Radar multi-occupancy detection
- Radar backwards compatibility
- Location narrative return json exception
- Disable datastream requests during playback
- Handle merging index, runtime and structure files from individual microservices when extending
- PF-1152 Daily Reports

### Added

- AGE-2 Responder organization user notification category
- Radar occupancy getters
- Allow choosing email passcode delivery type

## [9.5.3] - 2024-11-18

### Fixed

- PF-1206 Gateway broadband connection should handle loopback measurements
- botengine playback space type handling
- Squidlink Gateway handling of loopback network type
- Question Slider json structure
- Daily Report bedtime analysis

### Added
- Methods from parent class motion.py to motion_devloco.py
- PF-1208 Domain property to disable weekly/monthly daily reports
- Freezetime logic to demo microservice
- entry and motion devices rssi parameter trigger

## [9.5.2] - 2024-09-30

### Fixed
- BOT-1425 Exception handling and added debug info
- Botengine playback api keys may expire
- Botengine playback timestates should be published only after 2020-01-01

### Added
- Ability to save location priorities after bot playback
- Botengine playback can now publish/update/remove narratives upon completion (within 300 days)

## [9.5.1] - 2024-09-18

### Fixed
- Refactor location state publication after bot playback
- Admin url formatting
- Playback should support measurements that might have the same value described with each new measurement
- BOT-1416 Add datastream address to invoke service, fix category name
- Exception during bot playback

## [9.5.0] - 2024-07-25

### Added
- PF-1056 EngageKitCloud
- PF-1185 RAG Document Procesing
- Clear dashboard datastream address and tests
- BOT-1387 AI signal helper function to form text completion prompts
- BOT-1387 AI Api and llama model invocation

### Fixed
- BOT-1415 Condense vayyar subregions when submitting to device
- Botengine login method should work for bot development user and reference key expiration
- Tools datastream api url
- Logging
- Always sync modules when initializing the location
- BOT-1393 Daily Reports 
- BOT-1378 Update SMS items for delivery with entries after midnight
- Timezone getter
- User id comparison exception, test user information, and default timezone exception

## [9.4.2] - 2024-07-08

### Fixed
- Dashboard alarm cleanup should remove currently executed timestamps
- Loggers should describe warning and errors when logging by service name
- Botengine log export sorting
- Refactoring Apple Health device logic
- BOT-1410 Default cloud logging level
- Cloudwatch log exporter should handle broken log entries

### Changed
- Python runtime to 3.11

## [9.4.1] - 2024-06-07

### Fixed
- BOT-1397 Do not ask for ratings if iOS url is not none
- Do not trigger new version logic on first local run

## [9.4.0] - 2024-05-23

## [9.3.7] - 2024-05-23

### Fixed
- BOT-1379: Dashboard statuses expiration control
- Device microservice conversation type getter
- Tests and conversation signal handling
- Refactoring with additional action plan tests
- Bot exucution should stop if a valid start key is not provided
- Failed Botengine start process should not exit the function
- Bot bundle merge function should always include schedules

### Added
- BOT-1387: ai datastream address
- Researcher organization user notification category
- Error logging
- daylight tests

## [9.3.6] - 2024-04-30

### Fixed
- Daily Summary Report email should not be sent went the automated daily report service is disabled
- Include location name in Daily Summary Report email

### Added
- optional event_description to analytics signal to include in narrative
- Vayyar device doorEvent parameter trigger

## [9.3.5] - 2024-04-24

### Fixed
- Botengine Pytest module should provide complete location information during tests
- Sunrise and sunset times when no latitude or longitude
- Daily Report Summary should always email when automated services are enabled
- Playback input missing datastream feed error messaging
- botengine get_name_by_user_id may return None
- Maestro data transformation and csv enclosed quotes
- Add context to amplitude warning log

### Added
- Multistream logging

## [9.3.4] - 2024-04-02

### Fixed
- Botengine logging export
- Assign user id to device when loading controller
- Playback handling of location timeseries states

### Added
- device.last_user_id attribute

## [9.3.3] - 2024-03-26

### Fixed
- Botengine should gracefully handle no access
- Botengine playback should execute on all data_request triggers
- bedstatus param name reference
- logging exception
- Submit commands and integers

### Added
- Vayyar configurations

### Changed
- Vayyar subregions should be published to the device
- Update vayyar readme

## [9.3.2] - 2024-03-12

## [9.3.1] - 2024-03-08

### Fixed
- Organization tests
- Moved dailyreport, dashboard, daylight, machinelearning, and tasks to public signals and various other minor updates
- Lambda exception logging

### Added
- Sorting microservice intelligence modules by defining "execution_priority" in index.py
- Organization Bot submission management cli commands
- Bot Instance Log Export cli commands
- Device class firmware version helper functions

## [9.3.0] - 2024-02-27

### Added
- Botengine execution history cli command group
- OpenAI chat response handling during playback
- Smart Breaker device class
- Vayyar falling mitigator device method to enable/disable
- Daily Report services to support email and sms delivery
- Daily Report interpretation of insights and trends
- Location User Role enum

### Fixed
- Logging detail and specific services
- Question answer status handling
- Remove trailing slash on Care Daily API requests
- Daylight microservice should represent sunrise/sunset at current location timezome during playback
- Maestro data download should represent individual device start times

## [9.2.2] - 2024-01-31

### Fixed
- JSON handling and initial values in various botengine functionalities.
- Duplicate values and timer issues in location state fields and data request triggers.
- Several bugs and performance issues across bot measurement executions, analytics, statistics, insights, data streaming, python import exceptions, SMS delivery, video AI support, cloud server version checks, device type extraction, and logging.
- Error handling for question triggers, default runtime timeout adjustments, and other miscellaneous fixes.

### Changed
- Updated Python runtime to 3.9.
- Modifications to memory and runtime configurations, execution time limits, and asynchronous data requests for device startup and bot variables.

### Added
- Support for device message notifications, Withings Sleep device, and various signals for daily and weekly report entries.
- Execution statistics, Cloudwatch Logging for CLI, AWS Secret Manager support, utility methods for notifications, and enhancements to botengine playback features.
- CLI updates for runtime parameters, cloud version checks, scheduling supports, analytics timeout, ML error logging, push notification parameters, and the tag_release command.

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

## [8.2.0] - 2022-11-04

### Changed
- Python runtime to 3.9
- Moved memory and runtime fields from PUT developer/version to PUT developer/upload
- Limit execution time
- Asynchronous data request (device historical data) when bot start up
- Queue up device measurement and intelligence modules for follow-on executions
- Asynchronous for url request when bot start up(bot variables)

### Fixed
- Reduced some logging
- Data request need more time to wait to avoid the api request locked
- Include -b bundle_id parameter in pytest
- `--botinfo` check to get bot marketing information
- Do not attempt to purchase a committed bot if no location ID or organization ID is provided
- Use default device goal ID as defined by the bot if not set

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

[Unreleased]: https://github.com/caredailyai/botlab/compare/v9.3.0...HEAD
[9.3.0]: https://github.com/caredailyai/botlab/compare/v8.2.2...v9.3.0
[9.2.2]: https://github.com/caredailyai/botlab/compare/v8.2.0...v9.2.2
[9.0.6]: https://github.com/caredailyai/botlab/compare/v8.2.0...v9.0.6
[8.2.0]: https://github.com/caredailyai/botlab/tag/releases/v8.2.0