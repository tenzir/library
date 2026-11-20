---
title: Same Windows event data from every collector
type: change
authors:
  - zedoraps
created: 2026-11-19T12:12:30.415081Z
---

Security event data now carries the text of message-table tokens, and unnamed event data from legacy providers, such as Application Error, now uses the names `param1`, `param2`, … for all collectors, so Windows Event XML, Fluent Bit, and Winlogbeat produce the same event.

#### Message-table tokens

**Windows writes** (Security events in Windows Event XML):

```xml
<EventID>4826</EventID>  <Data Name="KernelDebug">%%1843</Data>          <!-- No -->
<EventID>4625</EventID>  <Data Name="FailureReason">%%2313</Data>       <!-- Unknown user name or bad password. -->
<EventID>4661</EventID>  <Data Name="AccessList">%%1537</Data>          <!-- DELETE -->
<EventID>4657</EventID>  <Data Name="NewValueType">%%1874</Data>        <!-- REG_EXPAND_SZ -->
<EventID>4719</EventID>  <Data Name="CategoryId">%%8272</Data>  <Data Name="AuditPolicyChanges">%%8448</Data>
```

Winlogbeat ships the text in the comments instead of the token.

**OCSF before → now:**

| Field | Before | Now |
|---|---|---|
| `unmapped.EventData.KernelDebug` (4826) | `%%1843` | `No` |
| `status_detail` (4625) | `%%2313` | `Unknown user name or bad password.` |
| `access_list` (4661, 4662) | `["%%1537"]` | `["DELETE"]` |
| `reg_value.type` (4657) | Not set | `REG_EXPAND_SZ` |
| 4719 `entity.policy.data` | `category_id: "%%8272"`, `changes: "%%8448"` | `category: "System"`, `changes: ["Success removed"]` |
| Winlogbeat 4657 activity | Unknown | Set, Modify, or Delete |

Free-text fields, such as command lines, and unknown tokens stay unchanged.

**Why:** a `%%` token points into the provider's message table. Windows Event XML and Fluent Bit report the tokens, while Winlogbeat reports the text, so the same event looked different per collector, and the mapping couldn't read the registry value type or the Winlogbeat registry operation.

#### Unnamed event data

**Windows writes** (Application Error 1000 on Windows Server 2022):

```xml
<Provider Name="Application Error"/>  <EventID>1000</EventID>
<Data>ReportViewer.exe</Data>   <!-- %1 in the message -->
<Data>4.12.307.2</Data>         <!-- %2 -->
<Data>65a1b2c3</Data>           <!-- %3 -->
```

**OCSF before → now:**

| Collector | Before | Now |
|---|---|---|
| Windows Event XML | `unmapped.EventData._0`, `_1`, … | `param1`, `param2`, … |
| Winlogbeat | `param1`, `param2`, … | Unchanged |

**Why:** legacy providers write their values without names, and the mappings read them as `param1`, `param2`, …, the names that Winlogbeat uses and that match the `%1`, `%2` inserts of the provider's message. Windows Event XML parsing numbered them from `_0`, so these mappings found nothing.

**What you need to do**

| Query | Effect | Replacement |
|---|---|---|
| Tests on a token, such as `%%1843` | Silent | Test the text, such as `No` |
| Tests on 4719 `category_id` or `subcategory_id` | Silent | Test `category` or `subcategory` |
| Tests on 4719 `changes` as a string | Silent | `"Success removed" in entity.policy.data.changes` |
| Tests on `unmapped.EventData._0` | Silent | Replace `unmapped.EventData._0` with `unmapped.EventData.param1`, and shift every other index by one |
