---
title: Traffic records from older PAN-OS versions without warnings
type: bugfix
authors:
  - zedoraps
created: 2026-11-27T13:21:51.118191Z
---

Traffic records with fewer columns than the current layout, such as the 115 columns that PAN-OS writes before 11.1, parse without a `csv parser found too few values` warning. Records shorter than the 65 columns of PAN-OS 8.1 keep the warning.
