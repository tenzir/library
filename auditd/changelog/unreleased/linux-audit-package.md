---
title: Linux Audit package
type: feature
authors:
  - zedoraps
created: 2026-11-26T23:59:32.014921Z
---

The new `auditd` package parses Linux Audit logs, assembles the records of each audit event, and maps the events to OCSF:

```tql
from_file "/var/log/audit/audit.log" {
  read_lines
}
auditd::ocsf::normalize
```

- `auditd::parse` reads the native `RAW` and `ENRICHED` formats and decodes hex-encoded values.
- `auditd::assemble` groups the records of one system call into one event.
- `auditd::ocsf::map` maps processes, files, network connections, logins, account changes, audit configuration, services, kernel extensions, and security module decisions.
