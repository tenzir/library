---
title: Decimal Windows access masks
type: bugfix
authors:
  - zedoraps
created: 2026-11-19T14:09:38.94251Z
---

Entity Management events now read a decimal `AccessMask` as decimal. Some 4674 records log the mask in decimal, such as `16777216` for `ACCESS_SYSTEM_SECURITY`, which the mapping read as hexadecimal and turned into `access_mask: 376926742`. A mask with a `0x` prefix is hexadecimal, and digits alone are decimal.

Rendered access rights set no `access_mask` and stay in `unmapped.EventData.AccessMask`.
