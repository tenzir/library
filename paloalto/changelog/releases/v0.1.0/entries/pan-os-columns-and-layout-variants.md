---
title: Exact PAN-OS column values and layout variants
type: bugfix
authors:
  - zedoraps
created: 2026-11-20T17:56:57Z
---

`paloalto::parse` now keeps text columns as PAN-OS writes them, reads the `AUTH`, `HIPMATCH`, Tunnel Inspection `START`/`END`, and lowercase `audit` records that it used to reject, keeps the columns of Correlated Events, Config, URL Filtering, and SD-WAN Traffic records in their documented positions, and `paloalto::ocsf::normalize` now also reads RFC 5424 Syslog messages.

**PAN-OS writes** (Traffic, with a rule name `00123` and SD-WAN link switches, abbreviated):

```
1,2026/05/29 11:00:01,000700000042,TRAFFIC,end,,2026/05/29 11:00:00,192.0.2.70,198.51.100.70,,,00123,…,{link-a, tag-a, ethernet1/1, 2026/05/29 10:59:58, 0, 0, N/A},…,general-internet,…,2026-05-29T11:00:00.250+02:00,…
```

**OCSF before → now:**

| | Before | Now |
|---|---|---|
| Rule name `00123`, filename `20260529` | Integer `123`, `20260529` (cast drops them) | `"00123"`, `"20260529"` |
| User agent or change detail with `;` | List of fragments | One string |
| `AUTH`, `HIPMATCH`, `START`, `END`, `audit` records | Not parsed, Base Event without fields | Parsed; `AUTH` and `audit` also mapped |
| Correlated Events severity and evidence | Shifted by one column; evidence dropped | `high`, evidence text |
| Config record without change details | Sequence number in `before_change_detail` | `sequence_number` |
| Traffic tail after SD-WAN link switches | Shifted by up to 8 columns | Documented positions |
| URL Filtering records of PAN-OS 10.1 and later (125 columns) | Shifted by two columns after the request headers | Documented positions, including `http_status_code` |
| Records with the documented columns of PAN-OS 9.1 or 10.0, such as 75 or 105 Traffic columns | Warning for every record | No warning; other short records keep it |
| Values beyond the documented columns | Dropped with a warning | `excess_values` |
| Times such as `2026-05-29T11:00:00.250+02:00` | Null in GlobalProtect records; `.250` as `.249999999` | Parsed with offset and exact milliseconds |
| High-resolution time `1969-12-31T16:00:00-08:00` | Unix epoch | Null |
| Syslog timestamp `May 29 11:00:05` | Event time, null after `ocsf_cast` | Only `unmapped.timestamp` |
| RFC 5424 Syslog message, such as `<14>1 2026-05-29T11:00:05+02:00 fw-example-1 - - - - 1,2026/05/29 11:00:01,…` | Not parsed, Base Event without fields | Parsed and mapped; zoned timestamp in `unmapped.timestamp` |

**Why:** PAN-OS writes every column as text, so guessing types turned identifiers into numbers and times. It writes SD-WAN link switches as an unquoted list with commas, Config records without change details have two columns fewer, and PAN-OS 10.1 added two URL Filtering columns in the middle of the record. Older PAN-OS versions write a documented prefix of the current columns. An RFC 3164 timestamp has neither year nor zone, so it can't be an event time. `parse_syslog` puts the payload of an RFC 5424 message into `message` instead of `content`, which the normalizer didn't read.
