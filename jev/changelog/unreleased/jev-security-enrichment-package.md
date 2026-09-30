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
`jev::ask` returns an `answers` record and an `answer_list` of answers with question
IDs. `jev::ask` sorts the list numerically for digit-only IDs, or alphabetically
otherwise. The windowed example pairs the sorted answers with events using
`zip` and unrolls each pair.

Configure the endpoint, model, and managed secret for your service, or pass
`api_key_secret_name=""` for a server without authentication.
`jev::collect_record` builds question records from collected key/value pairs
as a non-Nova workaround for the built-in `collect_record` function.

Requests run sequentially within each operator instance. To batch events in
one request, include each event in a separate question and submit the collected
question record with `jev::ask`.

Five examples demonstrate OCSF class suggestions, PII assessment of raw logs
and complete OCSF events, investigation priority, and windowed command-risk
scoring. Predictions support review and require validation on your own data
before automated decisions.
