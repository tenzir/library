---
title: Unify Fortinet package around FortiGate operators
type: breaking
authors:
  - mavam
  - codex
created: 2026-03-17T08:59:41.370501Z
---

The new `fortinet` package is now the entry point for Fortinet integrations, with FortiGate support namespaced under `fortinet::fortigate::*`. Existing installs must uninstall `fortinet-fortigate` before installing the new `fortinet` package.

Use the package to ingest framed FortiGate syslog and map it to OCSF:

```tql
subscribe "fortinet"
fortinet::fortigate::ocsf::map
publish "ocsf"
```

This replaces the previous `fortinet-fortigate` package layout and adds FortiGate parsing, cleanup, tests, and OCSF mappings for traffic, DNS, authentication, and selected security findings.
