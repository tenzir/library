---
title: OpenSSH package for Syslog and OCSF
type: feature
authors:
  - mavam
  - zedoraps
prs:
  - 175
created: 2026-08-17T00:00:00Z
---

The library now includes an `openssh` package for parsing OpenSSH `sshd`
messages. The package maps them to OCSF Authentication (class 3002), SSH
Activity (class 4007), Network Activity (class 4001), and Application Lifecycle
(class 6002).

The package exposes four operators. `parse` and `map` each take the field they
read and the field they write, in that order:

| Operator | Purpose |
|---|---|
| `openssh::ocsf::normalize` | Normalize one Syslog event carrying an `sshd` message |
| `openssh::parse` | Parse one raw `sshd` message into a structured OpenSSH event |
| `openssh::aggregate` | Optionally combine related parsed OpenSSH records |
| `openssh::ocsf::map` | Map a structured OpenSSH event to OCSF |

An `sshd` message carries neither a timestamp nor a host, so the normalizer
works on the Syslog event around it and takes both from there. It needs no
arguments:

```tql
accept_relp "0.0.0.0:2514"
this = data.parse_syslog()
where app_name in openssh::$app_names
openssh::ocsf::normalize
```

Pipelines that inspect or route the structured event can run each step
separately:

```tql
syslog = this
openssh::parse syslog.message, event, wide=true
event.syslog = syslog
openssh::aggregate syslog.message, event
openssh::ocsf::map event, ocsf
this = ocsf
```

The aggregation stage requires the parser's `wide=true` mode, which keeps all
messages on one schema.

The mapper carries the aggregated `raw_data` into the OCSF event itself.

`openssh::ocsf::map` consumes the source event. Mapped fields become OCSF
attributes, while source-specific fields remain under `unmapped`.
