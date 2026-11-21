---
title: Exact PAN-OS column values and layout variants
type: bugfix
authors:
  - zedoraps
created: 2026-11-20T17:56:57Z
---

`paloalto::parse` keeps PAN-OS columns exactly as written and places them correctly in more layouts; `paloalto::ocsf::normalize` also reads RFC 5424 Syslog.

```
1,2026/05/29 11:00:01,000700000042,TRAFFIC,end,,2026/05/29 11:00:00,192.0.2.70,198.51.100.70,,,00123,…,{link-a, tag-a, ethernet1/1, 2026/05/29 10:59:58, 0, 0, N/A},…
```

- Text columns stay text: rule `00123` and filename `20260529` no longer become integers, and a `;` no longer splits a user agent or change detail into a list.
- `AUTH`, `HIPMATCH`, Tunnel Inspection `START`/`END`, and lowercase `audit` records parse instead of yielding nothing.
- Correlated Events have separate source address and user columns, so severity and evidence are no longer shifted.
- Config records without change details, SD-WAN link switches with commas, and the 125-column URL Filtering layout of PAN-OS 10.1 and later keep every column in place.
- Records with the documented column counts of PAN-OS 8.1, 9.1, and 10.0, such as 65 Traffic or 75 Threat columns, no longer warn; other short records still do. Extra columns land in `excess_values`.
- Times with offsets, such as `2026-05-29T11:00:00.250+02:00`, parse with exact milliseconds; the Unix epoch placeholder of a missing high-resolution timestamp becomes null.
- An RFC 3164 Syslog timestamp no longer becomes the event time; Syslog timestamps stay in `unmapped.timestamp`.
