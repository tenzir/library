---
title: Removed Windows event mapping operators
type: breaking
authors:
  - zedoraps
created: 2026-11-20T08:29:20.791159Z
---

Three Windows event mapping operators are gone because their events now map to other OCSF classes. If you call them directly, switch to their replacements:

- `microsoft::windows::ocsf::events::application_crash_report` (Windows Error Reporting 1001) is now `microsoft::windows::ocsf::events::error_report`.
- `microsoft::windows::ocsf::events::eventlog_start` (6005) is now `microsoft::windows::ocsf::events::eventlog_service_state` with `activity_id=6`.
- `microsoft::windows::ocsf::events::eventlog_stop` (6006) is now `microsoft::windows::ocsf::events::eventlog_service_state` with `activity_id=7`.

The replacements take the same positional arguments, `windows` and `ocsf`. Pipelines that call `microsoft::windows::ocsf::normalize` need no change.
