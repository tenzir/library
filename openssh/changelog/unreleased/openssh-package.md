---
title: OpenSSH package for Syslog and OCSF
type: feature
authors:
  - mavam
  - claude
prs:
  - 175
created: 2026-08-17T00:00:00Z
---

The library now includes an `openssh` package for parsing OpenSSH `sshd`
messages and mapping them to OCSF Authentication (class 3002).

The package exposes three operators. Each takes its input as a positional
argument and writes to the named `into` argument, which defaults to `this`:

| Operator | Purpose |
|---|---|
| `openssh::ocsf::normalize` | Parse one raw `sshd` message body, map it, and store the body as `raw_data` |
| `openssh::parse` | Parse one raw `sshd` message body into a structured OpenSSH event |
| `openssh::ocsf::map` | Map a structured OpenSSH event to OCSF Authentication |

An `sshd` message body carries neither a timestamp nor a host, so the
normalizer takes both from the Syslog envelope:

```tql
accept_relp "0.0.0.0:2514"
this = data.parse_syslog()
where app_name == "sshd"
openssh::ocsf::normalize message, time=timestamp, hostname=hostname
```

Pipelines that inspect, enrich, or route the structured event call
`openssh::parse` and `openssh::ocsf::map` directly and assign `raw_data`
themselves.
