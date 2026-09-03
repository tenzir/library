# Verify collector receipt

Workload generation and collector delivery are separate outcomes. After all
probes, discover whether the configured exporter has a safe, already-authorized
query or capture surface. Never print OTLP credentials or headers.

1. Prefer an existing collector query API, local capture pipeline, or connected
   telemetry tool.
1. Account for export batching before querying. Claude Code flushes logs and
   metrics on an interval (`OTEL_LOGS_EXPORT_INTERVAL`, default 5000 ms, and
   `OTEL_METRIC_EXPORT_INTERVAL`, default 60000 ms), and the current session's
   final events flush only when it ends. Wait at least one export interval
   after the last probe, and treat a missing metric within the first minute as
   pending, not absent.
2. Query only the current run window and look for a fresh sentinel such as
   `harness-check-shell-success`, `harness-check-subagent`, or
   `harness-check-child-shell` plus the current harness service identity.
3. Record `telemetry.delivery.verified` as `PASS` only when a fresh event is
   observed. Include the event family and non-secret service identity.
4. Otherwise record `telemetry.delivery.unverified` as `SKIP` with the exact
   missing query endpoint, credentials, capture pipeline, or observed event.

Do not claim end-to-end delivery from exporter configuration, a successful
probe, or an event belonging to a different/concurrent run.
