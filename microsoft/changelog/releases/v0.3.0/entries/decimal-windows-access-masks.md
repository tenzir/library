---
title: Decimal Windows access masks
type: bugfix
authors:
  - zedoraps
created: 2026-11-19T14:09:38.94251Z
---

Entity Management events now read a decimal `AccessMask` as decimal.

| `AccessMask` | Before | Now |
|---|---|---|
| `16777216` (decimal, some 4674 records) | `access_mask: 376926742` | `access_mask: 16777216` |
| `0x12019f` | Hexadecimal | Hexadecimal |

Rendered access rights set no `access_mask` and stay in `unmapped.EventData.AccessMask`.
