---
title: Removed Windows event mapping operators
type: breaking
authors:
  - zedoraps
created: 2026-11-20T08:29:20.791159Z
---

Three operators under `microsoft::windows::ocsf::events::` are gone because their events now map to other OCSF classes.

| Removed operator | Replacement |
|---|---|
| `application_crash_report` (1001) | `error_report` |
| `eventlog_start` (6005) | `eventlog_service_state` with `activity_id=6` |
| `eventlog_stop` (6006) | `eventlog_service_state` with `activity_id=7` |

**Why:** the removed operators built Process Activity and Windows Service Activity events. Windows Error Reporting 1001 now maps to Application Error and Event Log 6005 and 6006 to Event Log Activity, which the replacements build.

**What you need to do:** Nothing if you call `microsoft::windows::ocsf::normalize`. If you call a removed operator directly, switch to its replacement, which takes the same positional arguments, `windows` and `ocsf`.
