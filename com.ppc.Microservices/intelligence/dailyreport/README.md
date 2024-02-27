# Daily Reports

This microservice creates a daily report for the user.
A signal can be received notifying this microservice that a new entry should be added to the daily report.
A signal is sent to notify other microservices that the daily report updated.

Supplementary services can be enabled from the UI using the Services and Alerts questions.

## Report Summaries

Interpret daily reports and produce SMS and Email summary reports for location users.

## Synthetic APIs

### Location States

#### Daily Report

Provides configuration information and settings that describe the service.

**name:** `dailyreport`

- `version` (String) Version of the daily report microservice
- `dailyreport.is_enabled` (Bool) Is the daily report service enabled
- `has_summary` (Bool) Summary microservice included in bundle
- `summary.is_enabled` (Bool) Summary service enabled

#### Daily Report Summary

Provides configuration information and settings that describe the service.

**name:** `dailyreport_summary`

### Time Series Location States

#### Daily Report

Accessible through the Care Daily mobile app, this is a time series location state the describes events for each individual day.

**name:** `dailyreport`

#### Weekly Report

Maintains historical data used for external services and stored for reference at weekly intervals. Keyed to the first day of the week (always Monday) local time.

**name:** `weeklyreport`

#### Monthly Report

Maintains historical data used for external services and stored for reference at monthly intervals.  Keyed to the last day of the month local time

**name:** `monthlyreport`

### Datastream Messages

#### Daily Report Entry

Datastream message to add a new entry to the daily report.

**name:** `daily_report_entry`

#### Daily Report Status Updated

Datastream message to notify other microservices that a report has been updated.

**name:** `daily_report_status_updated`

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
