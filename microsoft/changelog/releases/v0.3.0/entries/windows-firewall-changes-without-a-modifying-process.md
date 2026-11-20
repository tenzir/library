---
title: Windows Firewall changes without a modifying process
type: change
authors:
  - zedoraps
created: 2026-11-19T00:54:09.695523Z
---

Windows Firewall rule and configuration events (2003–2097) no longer build `actor.process`; the actor keeps the user from `ModifyingUser`.

| Field | Before | Now |
|---|---|---|
| `actor.process` | From `ModifyingApplication`, without `pid` | Not set |
| `unmapped.EventData.ModifyingApplication` | Not set | The image path |

**What you need to do**

| Rule | Effect | Replacement |
|---|---|---|
| New Firewall Rule Added In Windows Firewall Exception List Via WmiPrvSE.EXE | Silent | Match the unmapped field |
| A Rule Has Been Deleted From The Windows Firewall Exception List | Silent: its `ModifyingApplication: null` filter drops all events | Filter on the unmapped field |
| Exclusion-only rules, such as All Rules Have Been Deleted From The Windows Firewall Configuration | More alerts | Exclude on the unmapped field |

```tql
where metadata.log_name == "Microsoft-Windows-Windows Firewall With Advanced Security/Firewall" and
  metadata.event_code in ["2004", "2071", "2097"] and
  unmapped.EventData.ModifyingApplication.ends_with(r"\WmiPrvSE.exe")
```

**Why:** Windows Firewall logs no process ID, and an OCSF process needs one.
