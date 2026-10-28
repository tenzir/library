---
title: Schema-valid Windows and Graph observations
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:35.011614Z
prs:
  - 208
---

Windows and Microsoft Graph normalization now supplies required identifiers and preserves incomplete optional objects in unmapped data. Windows-specific fields identify the Windows extension. Activities lacking a required actor, device, process, entity, script, or peripheral identity become Base Events with the original mapping preserved under `unmapped.incomplete_activity`.

File activities without an identifiable file also become Base Events while retaining the observed context.
