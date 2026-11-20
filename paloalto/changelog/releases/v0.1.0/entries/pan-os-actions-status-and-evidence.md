---
title: Correct actions, status, and evidence in PAN-OS OCSF events
type: bugfix
authors:
  - zedoraps
created: 2026-11-20T17:56:57Z
---

PAN-OS Traffic, URL Filtering, and Threat events now map every documented action, report a status that matches the outcome, recognize lowercase HTTP methods, separate files from URLs, and leave out objects that the record doesn't identify.

**PAN-OS writes** (URL Filtering and Threat, abbreviated):

```
…,THREAT,url,…,tcp,block-url,coins.example.test/,(9999),cryptocurrency,…,"unknown, 203.0.113.8",…,propfind,…,"cryptocurrency,medium-risk",…
…,THREAT,virus,…,tcp,reset-both,20260529.exe,Example Virus Signature(400001),any,medium,server-to-client,7601,…
```

**OCSF before → now:**

| | Before | Now |
|---|---|---|
| `action_id`, `disposition_id` for `block-url`, `drop-all-packets`, `reset both`, `drop ICMP` | Not set | `2` (Denied) with Blocked, Dropped, or Reset |
| `block-continue`, `block-override` | Not set | `2` (Denied), Challenge |
| `sinkhole` | Not set | `2` (Denied), Blocked |
| Unknown action, such as `syncookie-sent` | Not set | `99` (Other) with the PAN-OS spelling |
| PAN-OS spelling of a mapped action | Dropped | `unmapped.action` |
| `status_id` of denied, dropped, reset, or blocked sessions and requests | `1` (Success) | `2` (Failure) |
| `status_id` of Traffic `start` and allowed URL requests | `1` (Success) | `0` (Unknown) |
| `activity_id` for method `get` | `0` (Unknown) | `3` (Get); `http_method: "GET"` |
| `http_request.x_forwarded_for` | String | List of addresses; original text in `unmapped` if it has other tokens |
| `http_request.url.categories` | PAN-DB label, rejected by `ocsf_derive` | `category_ids` such as `46` (News/Media), `[23, 24]` (Alcohol, Tobacco) for `alcohol-and-tobacco`; `99` (Other) with the label for categories without OCSF equivalent; risk ratings stay in `unmapped` |
| `connection_info` for protocol `6` | `protocol_name: 6` | `protocol_num: 6`, `protocol_name: "tcp"` |
| Filename of file, virus, and WildFire records | `evidences[].url.url_string` | `evidences[].file.name`, with the WildFire SHA-256 |
| `finding_info.title`, `analytic.name` | Filename and subtype | Signature name, such as `Example Virus Signature` |
| `finding_info.analytic.uid` | Whole column | Signature ID, such as `400001` |
| `is_alert` of a WildFire `benign` verdict | `true` | `false` |
| NAT `0.0.0.0` and port 0, empty user, rule, URL | Empty objects (warnings) | Omitted |
| `location` from a country name or address range | `desc` only (warning) | Omitted; value stays in `unmapped` |

**What you need to do:** Queries that count successful denied sessions or match PAN-DB labels in `categories` need an update. For example, replace `http_request.url.categories == ["news"]` with:

```tql
where 46 in http_request.url.category_ids
```

**Why:** PAN-OS names actions per log type and several map to the same OCSF disposition, writes HTTP methods in lowercase, and uses one URL/Filename column for both. The firewall's action says what it enforced, so a blocked session can't have succeeded, while an allowed URL request has no recorded response. OCSF requires typed addresses, category IDs, and identities for every object it contains.
