---
title: Windows authorize session OCSF mapping
type: feature
authors:
  - mavam
  - codex
prs:
  - 148
created: 2026-06-02T08:30:07.026165Z
---

The `microsoft::windows::ocsf::map` operator now maps Windows Security Event ID 4672, "Special privileges assigned to new logon", to OCSF Authorize Session (3003) with the Assign Privileges activity.
