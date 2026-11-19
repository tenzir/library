---
title: Kunai 0.7.0-rc.1 event layout
type: bugfix
authors:
  - mavam
created: 2026-11-09T12:18:01.074928Z
---

The `kunai::ocsf::map` operator now maps events of Kunai 0.7.0-rc.1, the current release. This version writes the user and group of a task directly into the `task` and `parent_task` sections instead of under `creds.effective`, and joins the process ancestors with `|` into a string instead of writing a list. The mapping now accepts both layouts, so the user of the process and its parent ends up in OCSF instead of in `unmapped`, and the process ancestry no longer goes missing.
