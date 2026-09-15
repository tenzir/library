---
title: Agent permissive mode detection
type: feature
authors:
  - claude
created: 2026-09-14T00:00:00.000000Z
---

The `tenzir` package now flags an agent session assigned a full-autonomy
permission or sandbox mode, such as Claude Code's `bypassPermissions` or
Codex's `danger-full-access` sandbox.

```tql
subscribe "ocsf"
tenzir::detect::agent::permissive_mode
publish "findings"
```

The detector is a static policy check on the currently-assigned privileges,
independent of how or why the mode was assigned — it fires the same whether a
person chose it deliberately or a repo's checked-in configuration set it.

Detectors live in the `tenzir::detect::agent` namespace, alongside
`tenzir::detect::network` and `tenzir::detect::behavior`. Every finding
carries MITRE ATT&CK tactic and technique mappings in `finding_info.attacks`
and a versioned analytic identity for traceability.
