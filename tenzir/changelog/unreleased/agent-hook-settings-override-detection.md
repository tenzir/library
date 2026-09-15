---
title: Agent hook settings-override detection
type: feature
authors:
  - claude
created: 2026-09-14T00:00:00.000000Z
---

The `tenzir` package now flags a Claude Code hook registered through a CLI
or deeplink settings override (`hook_source == "flagSettings"`) rather than
a committed project or user settings file.

```tql
subscribe "ocsf"
tenzir::detect::agent::hook_settings_override
publish "findings"
```

This settings tier ranks above committed project and user files in Claude
Code's precedence order, and is the mechanism behind `CVE-2025-59536` and
`CVE-2026-21852` ("Caught in the Hook", Check Point Research), both fixed
upstream (`1.0.111+` and `2.0.65+` respectively). The detection remains
useful for unpatched installs and as an audit signal for how a session's
hooks were assigned.
