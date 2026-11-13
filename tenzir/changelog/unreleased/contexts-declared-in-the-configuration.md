---
title: Contexts declared in the configuration
type: breaking
authors:
  - mavam
created: 2026-11-13T11:28:40.375682Z
---

The package no longer ships the `process-name-baselines` context, and
`tenzir::osint::update_context` no longer takes `max_age`, because Tenzir 7
declares contexts and their timeouts in the configuration. Declare both lookup
tables there:

```yaml
# contexts/ocsf-osint.yaml
type: lookup-table
persist-interval: 5min
write-timeout: 30d
```

```yaml
# contexts/process-name-baselines.yaml
type: lookup-table
persist-interval: 5min
```

Before:

```tql
tenzir::osint::update_context max_age=30d
```

After:

```tql
tenzir::osint::update_context
```

Since a context can't erase entries, a removed indicator now replaces its entry
with one that has already expired, and `tenzir::osint::enrich` ignores it.
