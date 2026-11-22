---
title: NULL SID no longer becomes a Windows user
type: bugfix
authors:
  - zedoraps
prs:
  - 261
created: 2026-11-22T12:00:11.559534Z
---

The NULL SID (`S-1-0-0`, or `NULL SID` from collectors that translate SIDs) no longer becomes `user.uid` or `actor.user.uid`. 4624/4625 without a subject get no `actor`, and 4625 without a target account gets no `user`.
