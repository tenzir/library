---
title: Jev security enrichment package
type: feature
authors:
  - zedoraps
prs:
  - 189
created: 2026-09-30T07:54:13.846764Z
---

The Jev package adds typed questions about security logs through Jev and
compatible System One APIs, including local Laya. Ask a single probability
question with `jev::noul`:

```tql
from {raw: "Login succeeded for alex.morgan@example.com"}
jev::noul "Does this log contain personal data?", state=raw
```

Use `jev::choice` to select among named options, `jev::score` to assess ordered
criteria, or `jev::ask` to submit multiple questions in one request. The
single-question operators return a complete `answer` record and request `usage`.

Configure the endpoint, model, and managed secret for your service, or pass
`api_key_secret_name=""` for a server without authentication. `jev::ask_batch` submits
independent states to compatible batch endpoints, and `jev::collect_record`
builds question records from collected key/value pairs.

Requests run sequentially within each operator instance. Native batching
assesses multiple independent states in a single request.

Five examples demonstrate OCSF class suggestions, PII assessment of raw logs
and complete OCSF events, and investigation priority. Predictions support
review and require validation on your own data before automated decisions.
