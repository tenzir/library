# Collect coding-agent telemetry

The OpenTelemetry package receives OTLP/HTTP JSON or Protobuf from coding
agents on port `4318`. Install the `otel` package and the vendor packages you
need, then enable these pipelines in the Tenzir Platform:

- **Receive OTLP over HTTP**
- **Normalize Codex OTLP to OCSF** and/or **Normalize Claude Code OTLP to OCSF**

The receiver uses `schema="record"` so the vendor packages can access OTLP
attributes by their literal keys. You can also configure the receiver as a
pipeline in `tenzir.yaml`:

```yaml
tenzir:
  pipelines:
    otlp-receiver:
      name: OTLP Receiver
      definition: |
        accept_otlp "0.0.0.0:4318", schema="record"
        publish "otlp"
      restart-on-error: 30s
```

If the node runs in Docker, publish port `4318`:

```yaml
ports:
  - "4318:4318"
```

## Configure Codex

Add the following to `~/.codex/config.toml`:

```toml
[otel]
environment = "production"
log_user_prompt = false
exporter = { otlp-http = { endpoint = "http://localhost:4318/v1/logs", protocol = "json" } }
trace_exporter = { otlp-http = { endpoint = "http://localhost:4318/v1/traces", protocol = "json" } }
metrics_exporter = "none"
```

See the [Codex observability documentation](https://learn.chatgpt.com/docs/config-file/config-advanced#observability-and-telemetry).

## Configure Claude Code

Set these environment variables before starting Claude Code:

```sh
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1
export OTEL_LOGS_EXPORTER=otlp
export OTEL_TRACES_EXPORTER=otlp
export OTEL_METRICS_EXPORTER=none
export OTEL_EXPORTER_OTLP_PROTOCOL=http/json
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
export OTEL_LOG_TOOL_DETAILS=1

claude
```

See the [Claude Code monitoring documentation](https://code.claude.com/docs/en/monitoring-usage).

Replace `localhost` with the node hostname when the agent runs on another
machine. Prompt text and tool details can contain source code, credentials, and
other sensitive data, so enable content collection only when your retention and
access policies permit it.
