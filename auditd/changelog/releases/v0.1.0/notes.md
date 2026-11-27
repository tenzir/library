The new auditd package parses Linux Audit logs, assembles the records of each audit event, combines the records of a login into one event, and maps the events to OCSF 1.9.

## 🚀 Features

### Linux Audit package

The new `auditd` package parses Linux Audit logs, assembles the records of each audit event, and maps the events to OCSF:

```tql
from_file "/var/log/audit/audit.log" {
  read_lines
}
auditd::ocsf::normalize
```

- `auditd::parse` reads the native `RAW` and `ENRICHED` formats and decodes hex-encoded values.
- `auditd::assemble` groups the records of one system call into one event.
- `auditd::aggregate` combines the PAM records of one login into one logon, account switch, or logoff.
- `auditd::adapters::journal` rebuilds audit records from systemd journal entries.
- `auditd::ocsf::map` maps processes, files, network connections, logins, account changes, audit configuration, services, kernel extensions, and security module decisions.

*By @zedoraps.*
