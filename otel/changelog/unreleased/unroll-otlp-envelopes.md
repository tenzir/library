---
title: Unroll OTLP logs and traces
type: feature
authors:
  - philip
components:
  - otel
created: 2026-07-29T00:00:00Z
---

The OpenTelemetry package can receive decoded OTLP events through the native
`accept_otlp` operator. A disabled receiver pipeline publishes `otel.log`,
`otel.span`, and `otel.metric.*` events to the `otlp` topic with record-shaped
attributes.

The package retains `otel::decode_attributes`, `otel::unroll_logs`, and
`otel::unroll_traces` for pipelines that still receive OTLP/JSON export
envelopes through generic HTTP inputs. New pipelines should use `accept_otlp`
instead.

The compatibility unrolling operators accept a `jobs` argument to decode
individual records in parallel. Duplicate attribute keys are preserved as
lists, identifier values remain strings, and exporter-generated `"null"`
placeholders do not override typed values.

Product-specific normalization belongs to vendor packages.
