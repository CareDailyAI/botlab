# Daily Reports

This microservice creates a daily report for the user.
A signal can be received notifying this microservice that a new entry should be added to the daily report.
A signal is sent to notify other microservices that the daily report updated.
A signal can be received describing new configurations for the daily report.

Supplementary services can be enabled from the UI using the Services and Alerts questions.

## Wellness Reports

Interpret daily reports and produce GPT reports.

This microservce coordinates report generation based on Activities of Daily Living and other data.
Accumulated daily, weekly, and monthly, the report content is distributed to LLM Services (i.e., OpenAI ChatGPT) for analysis and generation of 1 or more reports based on user roles at this location.
Reports are distributed to the user's preferred communication channel at appropriate times, and can be available on command.

Reports are disabled by default, and can be enabled from the UI using the Services and Alerts questions.

### Report Types

Report Types are used to describe the characteristics/rules associated with the ChatGPT ChatCompletion APIs, as well as coordinate the delivery of created reports.

## Report Summaries

Interpret daily reports and produce SMS and Email summary reports for location users.

## Synthetic APIs

### Location States

#### Daily Report

Provides configuration information and settings that describe the service.

**name:** `dailyreport`

- `version` (String) Version of the daily report microservice
- `dailyreport.is_enabled` (Bool) Is the daily report service enabled
- `has_gpt` (Bool) GPT microservice included in bundle
- `gpt.is_enabled` (Bool) GPT service enabled
- `has_summary` (Bool) Summary microservice included in bundle
- `summary.is_enabled` (Bool) Summary service enabled
- `section_config` (Dict) Describes changes to default section properties

#### Daily Report GPT

Provides configuration information and settings that describe the service.

**name:** `dailyreport_gpt`

- `report_types` (Array) List of json objects describing hows the service should interpret reports
    - `id` (Int) Unique Report Type ID
    - `role_type` (Int) Role Type ID (users.user.ROLE_TYPE_*)
    - `role` (String) Name of the role
    - `rules` ([String]) Rules for this role
    - `supported_section_ids` ([Int]) Supported section IDs (See dailyreport.SECTION_ID_*)
    - `supported_trend_ids` ([String]) Supported trend IDs
    - `supported_insight_ids` ([String]) Supported insight IDs
- `system_rules` ([String]) System rules

#### Daily Report Summary

Provides configuration information and settings that describe the service.

**name:** `dailyreport_summary`

### Time Series Location States

#### Daily Report

Accessible through the Care Daily mobile app, this is a time series location state the describes events for each individual day.  When enabled, GPT Reports for weekly and monthly responses described to the Primary Caregiver role type are included in the Daily Report.

**name:** `dailyreport`

#### Weekly Report

Maintains historical data used for generating weekly GPT Reports and stored for reference at weekly intervals. Keyed to the first day of the week (always Monday) local time.

**name:** `weeklyreport`

#### Monthly Report

Maintains historical data used for generating monthly GPT Reports and stored for reference at monthly intervals.  Keyed to the last day of the month local time

**name:** `monthlyreport`

### Datastream Messages

#### Daily Report Entry

Datastream message to add a new entry to the daily report.

**name:** `daily_report_entry`

#### Daily Report Status Updated

Datastream message to notify other microservices that a report has been updated.

**name:** `daily_report_status_updated`

#### Update Daily Report GPT Report Types

Datastream message to configure daily report types.

**name:** `update_daily_report_gpt_report_types`

#### Set Daily Report Configuration

Datastream message to set configurations

**name:** `daily_report_set_config`

### Signals

Supplementary microservices can update the Daily Report microservice using the dailyreport signal method.

For specific requirements, see `com.ppc.Bot/signals/dailyreport.py`.

#### Add Entry

Add a section and bullet point the current daily report.

#### Add Weekly Entry

Add a section and bullet point the current weekly report.

#### Add Monthly Entry

Add a section and bullet point the current monthly report.

#### Report Status Updated

Notify supplementary microservices that a report status has changed.

#### Set Section Config

Set the daily report section configuration.