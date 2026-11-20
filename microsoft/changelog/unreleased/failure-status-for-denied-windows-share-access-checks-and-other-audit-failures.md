---
title: Failure status for denied Windows share access checks and other audit failures
type: bugfix
authors:
  - zedoraps
created: 2026-11-20T19:10:46.430307Z
---

Denied network share access checks and other Windows Security events that Windows logs as audit failures now have status Failure instead of Success.

**Windows writes** (Security 5145, denied):

```xml
<EventID>5145</EventID>
<Keywords>0x8010000000000000</Keywords>  <!-- Audit Failure -->
<Data Name="AccessReason">%%4417:	%%1805</Data>  <!-- WriteData (or AddFile): Not granted -->
```

**What changes:**

- Denied 5145 checks now have status Failure instead of Success, with the reason in `status_detail`, such as `WriteData (or AddFile):	Not granted`.
- Share access (5140) and account mapping (4774) now take their status from the audit keywords: Audit Failure is Failure, Audit Success is Success.
- Kerberos TGT requests (4768) without a result code take their status from the audit keywords instead of Failure.
- Events without known audit keywords now have status Unknown instead of Success, including handle requests (4656) and object access (4663).
- Events that Windows logs only on success keep status Success: startup (4608), process creation (4688) and exit (4689), session reconnects (4778) and disconnects (4779), and security package loads (4610, 4611, 4614, 4622).
