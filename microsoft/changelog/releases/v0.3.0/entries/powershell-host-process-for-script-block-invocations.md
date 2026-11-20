---
title: PowerShell host process for script block invocations
type: bugfix
authors:
  - zedoraps
created: 2026-11-18T10:40:15.169836Z
---

PowerShell script block invocation starts and stops (4105/4106) now set `actor.process` to the PowerShell host's `pid` and `ptid`, like script block logging (4104).
