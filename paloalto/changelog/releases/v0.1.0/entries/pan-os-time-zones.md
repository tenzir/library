---
title: Time zone of PAN-OS times
type: feature
authors:
  - zedoraps
created: 2026-11-20T19:30:00Z
---

`paloalto::parse` and `paloalto::ocsf::normalize` now take an optional `timezone` argument for PAN-OS times without a zone, and use the offset of the high-resolution timestamp when you don't set it.

**PAN-OS writes** (System, abbreviated):

```
1,2026/07/15 10:00:01,000700000042,SYSTEM,general,,2026/07/15 10:00:00,…,2026-07-15T10:00:01.250+02:00
```

**OCSF before → now:**

| | Before | Now |
|---|---|---|
| `time` of `2026/07/15 10:00:00` | `2026-07-15T10:00:00Z` | `2026-07-15T08:00:00Z`, from the offset `+02:00` |
| With `timezone="Europe/Berlin"` | Not available | `2026-07-15T08:00:00Z` in summer, `09:00:00Z` in winter |
| Without `timezone` or high-resolution timestamp | UTC | UTC |

**What you need to do:** Set the firewall's time zone when its records lack a high-resolution timestamp:

```tql
paloalto::ocsf::normalize timezone="Europe/Berlin"
```

An IANA name accounts for daylight saving time, while a fixed offset such as `+01:00` applies to every record.

**Why:** PAN-OS writes most times in the firewall's time zone without naming it, but writes the high-resolution timestamp with its UTC offset.
