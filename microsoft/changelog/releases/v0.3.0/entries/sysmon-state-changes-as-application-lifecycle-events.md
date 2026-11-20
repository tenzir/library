---
title: Sysmon state changes as Application Lifecycle events
type: change
authors:
  - zedoraps
created: 2026-11-19T01:01:49.320307Z
---

Sysmon service state changes (4) now map to Application Lifecycle (6002) with the Start or Stop activity, and the Sysmon service with its version in `application`.

The event names neither the service configuration nor a process or account that changed the state. Windows Service Activity requires both a `win_service` with service details and an `actor`, so `ocsf_cast` warned about these events.

Tenzir's Sigma catalog has no family for the `sysmon_status` category, so no Sigma rule depends on the previous class.
