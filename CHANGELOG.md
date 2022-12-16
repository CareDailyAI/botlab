All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [8.2.0] - 2022-11-04

### Fixed
- Reduced some logging
- Data request need more time to wait to avoid the api request locked

### Changed
- Python runtime to 3.9
- Moved memory and runtime fields from PUT developer/version to PUT developer/upload
- Limit execution time
- Asynchronous data request (device historical data) when bot start up
- Queue up device measurement and intelligence modules for follow-on executions
- Asynchronous for url request when bot start up(bot variables)

### Fixed
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

[Unreleased]: https://github.com/caredailyai/botlab/compare/v8.2.0...HEAD
[8.2.0]: https://github.com/caredailyai/botlab/tag/releases/v8.2.0
