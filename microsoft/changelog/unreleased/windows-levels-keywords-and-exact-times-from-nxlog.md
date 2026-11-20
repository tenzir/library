---
title: Windows levels, keywords, and exact times from NXLog
type: change
authors:
  - zedoraps
created: 2026-11-20T17:43:53.990321Z
---

Windows events from NXLog now carry the level, keywords mask, provider GUID, and activity ID in the form that Windows writes, and read times that NXLog writes as microseconds since the Unix epoch exactly.

**NXLog writes** (Community Edition, `to_json()`):

```json
{"EventTime": "2026-03-26 03:11:05", "EventType": "AUDIT_SUCCESS", "Keywords": -9214364837600034816,
 "ProviderGuid": "{54849625-5478-4994-A5BA-3E3B0328C30D}", "ActivityID": "{6B1E07C4-2A9D-0003-5F7A-C14E2B9D7A02}"}
```

**OCSF before → now:**

| Field | Before | Now |
|---|---|---|
| `metadata.log_level` | Not set | `0` for `AUDIT_SUCCESS` and `AUDIT_FAILURE`, `1` to `5` for `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `VERBOSE` |
| `severity_id` (PowerShell 4104 warnings) | Informational | Low, as for natively collected events |
| `unmapped.System.Keywords` | `-9214364837600034816` | `"0x8020000000000000"` |
| `metadata.product.uid` | `{54849625-5478-4994-A5BA-3E3B0328C30D}` | `{54849625-5478-4994-a5ba-3e3b0328c30d}` |
| `metadata.correlation_uid` | Not set, `unmapped.NXLog.activity_uid` | `{6b1e07c4-2a9d-0003-5f7a-c14e2b9d7a02}` |
| `time`, `metadata.logged_time` from integer `EventTime` and `EventReceivedTime` | Not set (warning) | Exact to the microsecond |
| `time`, `metadata.logged_time` from strings that the JSON reader keeps, such as with `parse_json(raw=true)` | Not set (warning) | The local time, read as UTC |

**What you need to do**

NXLog Community Edition writes `EventTime` and `EventReceivedTime` in the local time of the Windows host, without a time zone and with second precision, which read as UTC. For exact times, let NXLog write microseconds since the Unix epoch:

```
<Input eventlog>
  Module im_msvistalog
  Exec $EventTime = integer($EventTime); $EventReceivedTime = integer($EventReceivedTime);
</Input>
```

Read NXLog's JSON with `parse_json(raw=true, unflatten_separator=".")`, so that event data values stay as NXLog writes them instead of guessed types, such as a time for the `ProcessCreationTime` of Security 5379.

**Why:** NXLog Community Edition writes no level and renders the keywords mask as a signed integer, so mappings that read the level or the audit outcome saw nothing or a different value than for natively collected events.
