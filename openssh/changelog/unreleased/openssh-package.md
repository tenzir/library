---
title: OpenSSH package for Syslog and OCSF
type: feature
authors:
  - mavam
prs:
  - 175
created: 2026-08-17T00:00:00Z
---

The library now includes an `openssh` package for parsing OpenSSH `sshd`
messages and mapping them to OCSF Authentication (class 3002).

The package exposes three operators. `parse` and `map` each take the field they
read and the field they write, in that order:

| Operator | Purpose |
|---|---|
| `openssh::ocsf::normalize` | Take a Syslog event carrying an `sshd` message all the way to OCSF |
| `openssh::parse` | Parse one raw `sshd` message into a structured OpenSSH event |
| `openssh::ocsf::map` | Map a structured OpenSSH event to OCSF Authentication |

An `sshd` message carries neither a timestamp nor a host, so the normalizer
works on the Syslog event around it and takes both from there. It needs no
arguments:

```tql
accept_relp "0.0.0.0:2514"
this = data.parse_syslog()
where app_name == "sshd"
openssh::ocsf::normalize
```

Pipelines that inspect, enrich, or route the structured event stage the steps
themselves:

```tql
// 1. Parse: the opaque message becomes a structured OpenSSH event.
openssh::parse message, event
// 2. Stage: the envelope contributes what the message body cannot carry.
event.time = move timestamp
event.hostname = move hostname
// 3. Map: the OpenSSH event becomes minimal OCSF Authentication.
openssh::ocsf::map event, ocsf
// 4. Embed: the caller decides that the message is the event's provenance.
this = {...ocsf, raw_data: message}
```

`openssh::ocsf::map` consumes the source event: what it maps becomes OCSF, and
what it cannot map becomes `unmapped` inside the OCSF event.
