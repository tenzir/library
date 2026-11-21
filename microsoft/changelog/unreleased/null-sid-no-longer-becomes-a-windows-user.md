---
title: NULL SID no longer becomes a Windows user
type: bugfix
authors:
  - zedoraps
created: 2026-11-20T19:28:18.198851Z
---

The NULL SID (`S-1-0-0`, or `NULL SID` from SID-translating collectors) in a SID field no longer becomes a user.

- `user.uid` and `actor.user.uid` no longer hold it; names and other values stay.
- 4624/4625 without a subject get no `actor`; 4625 without a target account gets no `user`.
- ASIM no longer reports it as `ActorUsername`/`ActorUserId`.
