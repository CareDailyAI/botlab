All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [9.2.2] - 2024-01-31

#### Fixed
- JSON handling and initial values in various botengine functionalities.
- Duplicate values and timer issues in location state fields and data request triggers.
- Several bugs and performance issues across bot measurement executions, analytics, statistics, insights, data streaming, python import exceptions, SMS delivery, video AI support, cloud server version checks, device type extraction, and logging.
- Error handling for question triggers, default runtime timeout adjustments, and other miscellaneous fixes.

#### Changed
- Updated Python runtime to 3.9.
- Modifications to memory and runtime configurations, execution time limits, and asynchronous data requests for device startup and bot variables.

#### Added
- Support for device message notifications, Withings Sleep device, and various signals for daily and weekly report entries.
- Execution statistics, Cloudwatch Logging for CLI, AWS Secret Manager support, utility methods for notifications, and enhancements to botengine playback features.
- CLI updates for runtime parameters, cloud version checks, scheduling supports, analytics timeout, ML error logging, push notification parameters, and the tag_release command.

[Unreleased]: https://github.com/caredailyai/botlab/compare/v9.2.2...HEAD
[9.2.2]: https://github.com/caredailyai/botlab/tag/releases/v9.2.2
