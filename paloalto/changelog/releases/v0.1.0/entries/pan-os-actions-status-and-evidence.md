---
title: Correct actions, status, and evidence in PAN-OS OCSF events
type: bugfix
authors:
  - zedoraps
created: 2026-11-20T17:56:57Z
---

PAN-OS Traffic, URL Filtering, and Threat events now map actions, status, HTTP details, and threat evidence correctly.

| | Before | Now |
|---|---|---|
| `block-url`, `drop-all-packets`, `reset both`, `drop ICMP`, `sinkhole` | No action | Denied with Blocked, Dropped, or Reset |
| `block-continue`, `block-override` | No action | Denied, Challenge |
| Unknown action, such as `syncookie-sent` | No action | Other with the PAN-OS spelling |
| PAN-OS spelling of an action | Dropped | `unmapped.action` |
| Status of blocked sessions and requests | Success | Failure |
| Status of Traffic `start` and allowed URL requests | Success | Unknown |
| HTTP method `get` | Unknown activity | Get, `http_method: "GET"` |
| X-Forwarded-For | String | List of addresses |
| PAN-DB categories | Labels, rejected by `ocsf_derive` | `category_ids`, such as `46` (News/Media); Other with the label when OCSF has no equivalent; risk ratings stay in `unmapped` |
| Protocol `6` | `protocol_name: 6` | `protocol_num: 6`, `protocol_name: "tcp"` |
| Filename of file, virus, and WildFire records | URL evidence | File evidence, with the WildFire SHA-256 |
| Finding title and analytic | Filename, subtype, whole column | Signature name and ID |
| WildFire `benign` verdict | Alert | Not an alert |
| NAT `0.0.0.0`, empty user, rule, or URL, location from a country name | Empty objects | Omitted; the value stays in `unmapped` |
