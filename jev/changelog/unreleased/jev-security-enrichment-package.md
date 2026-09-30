---
title: Jev security enrichment package
type: feature
authors:
  - zedoraps
prs:
  - 189
created: 2026-09-30T07:54:13.846764Z
---

The Jev package adds typed questions about security logs through Jev and compatible System One APIs, including local Laya. Use `jev::ask` to add answers to an event:

```tql
from {raw: "Login succeeded for alex.morgan@example.com"}
questions = {pii: {
  type: "noul",
  instructions: "Does this log contain personal data?",
}}
jev::ask questions, state=raw
```

Configure the endpoint, model, and managed secret for your service, or pass `api_key=""` for a server without authentication. `jev::ask_batch` submits independent states to compatible batch endpoints, and `jev::collect_record` builds question records from collected key/value pairs.

Four examples demonstrate OCSF class suggestions and PII assessment of raw logs and complete OCSF events. Predictions support review and require validation on your own data before automated decisions.
