---
title: Add OpenTelemetry log export package
type: change
authors:
  - mavam
components:
  - otel
created: 2026-03-13T08:25:41Z
---

Added an experimental `otel` package for reshaping Tenzir events into OTLP JSON
logs payloads.

The package includes three user-defined operators:

- `otel::attributes` to convert a record into OTLP `KeyValue[]`
- `otel::logrecord` to build one OTLP `LogRecord`
- `otel::export_logs` to wrap a log record in an OTLP logs export payload

The package also includes tests covering attribute conversion, log record
construction, OTLP envelope generation, and an end-to-end ESXi syslog example.
