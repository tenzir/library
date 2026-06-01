---
title: OpenTelemetry log export package
type: change
authors:
  - mavam
components:
  - otel
prs:
  - 147
created: 2026-03-13T08:25:41Z
---

The new experimental OpenTelemetry package can reshape Tenzir events into OTLP
JSON logs payloads.

Use the package when you need to send normalized events to an OTLP-compatible
log collector. It includes three operators:

- `otel::attributes` to convert a record into OTLP `KeyValue[]`
- `otel::logrecord` to build one OTLP `LogRecord`
- `otel::export_logs` to wrap a log record in an OTLP logs export payload

For example, build a log record and wrap it for export:

```tql
otel::logrecord
otel::export_logs
```
