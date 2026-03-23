---
title: Sysmon package with OCSF mapping
type: feature
authors:
  - mavam
  - claude
pr: 78
created: 2026-03-23T01:59:56.804658Z
---

Adds a new `sysmon` package that parses Sysmon XML events and maps them to OCSF.

The package provides two operators:

- `sysmon::ocsf::map <field>` — parses a raw Sysmon XML field and maps it to
  OCSF. Currently maps Event ID 1 (Process Create) to OCSF Process Activity
  (class 1007). All other event IDs fall back to OCSF Base Event (class 0) with
  remaining fields in `unmapped`.
- `sysmon::ocsf::events::process_create` — internal sub-operator for the EID 1
  mapping (exposed for composition).

Typical usage after ingesting Sysmon Windows Event Log XML:

```tql
sysmon::ocsf::map data
this = ocsf
ocsf::derive
ocsf::cast
```

Test fixtures covering all 29 Sysmon event types (EID 1–29) ship with the
package so mapping coverage can be validated with `tenzir-test`.
