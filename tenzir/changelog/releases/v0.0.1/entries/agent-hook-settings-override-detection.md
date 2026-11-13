---
title: Agent hook settings-override detection
type: feature
authors:
  - claude
created: 2026-09-14T00:00:00.000000Z
---

The `tenzir` package now flags a Claude Code hook registered through a CLI
settings override (`hook_source == "flagSettings"`) rather than a
committed project or user settings file.

```tql
subscribe "ocsf"
tenzir::detect::agent::hook_settings_override
publish "findings"
```

This settings tier ranks above committed project and user files in Claude
Code's precedence order, populated by the documented `--settings` CLI
flag. That's a legitimate, documented automation mechanism, so expect
this to fire on CI/CD and scripted invocations; it's best read as an
audit signal for interactive sessions, not a universal severity claim.
