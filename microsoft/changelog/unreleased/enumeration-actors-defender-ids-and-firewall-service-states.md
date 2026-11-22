---
title: Enumeration actors, Defender IDs, and firewall service states
type: change
authors:
  - zedoraps
prs:
  - 261
created: 2026-11-22T12:00:12.317836Z
---

More Windows details map to OCSF:

- 4797–4799: the subject as `actor`, and the caller process for 4798/4799.
- Defender 1116/1117: the threat ID in `malware[].uid`, and the platform version in `metadata.product.version`.
- Firewall and IPsec service events 5025, 5030, 5034, 5035, and 5478: Application Lifecycle instead of Base Event.
