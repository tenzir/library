---
title: Windows Firewall and IPsec service state in OCSF
type: change
authors:
  - zedoraps
created: 2026-11-21T11:38:27.244965Z
---

More Windows Firewall and IPsec service events map to OCSF Application Lifecycle instead of Base Event.

- 5025/5034 (stopped): activity Stop.
- 5030/5035 (failed to start): activity Start, status Failure.
- 5478 (IPsec Services started): activity Start.
