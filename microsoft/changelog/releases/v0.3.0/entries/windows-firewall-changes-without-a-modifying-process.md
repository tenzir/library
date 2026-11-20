---
title: Windows Firewall changes without a modifying process
type: change
authors:
  - zedoraps
created: 2026-11-19T00:54:09.695523Z
---

Windows Firewall rule and configuration events (2003–2097) no longer build `actor.process` from `ModifyingApplication`. The path stays in `unmapped.EventData.ModifyingApplication`, and the actor keeps the modifying user from `ModifyingUser`.

Windows Firewall names the modifying application only by its image path and logs no process ID. An OCSF process needs a `pid`, `uid`, or `cpid`, so `ocsf_cast` warned about these events.

Tenzir's Sigma catalog reads `ModifyingApplication` from `actor.process.path`, so Sigma rules that test it now see no value:

- *New Firewall Rule Added In Windows Firewall Exception List Via WmiPrvSE.EXE* no longer matches.
- *A Rule Has Been Deleted From The Windows Firewall Exception List* filters out every event through its `ModifyingApplication: null` filter.
- Rules that only exclude applications, such as *All Rules Have Been Deleted From The Windows Firewall Configuration*, now also match the excluded applications.

Match the application on the unmapped field instead:

```tql
where metadata.log_name == "Microsoft-Windows-Windows Firewall With Advanced Security/Firewall" and
  metadata.event_code in ["2004", "2071", "2097"] and
  unmapped.EventData.ModifyingApplication.ends_with(r"\WmiPrvSE.exe")
```
