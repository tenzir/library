---
title: Source context preservation in Suricata OCSF events
type: bugfix
prs:
  - 217
created: 2026-11-04T15:28:49.994681Z
---

Suricata normalization now supplies Unknown direction and device types for reported connection and host context. DNS SOA and SRV records expose their resource data, while DNS records without resource data and partial HTTP or TLS details retain their original keys under `unmapped`.

Optional HTTP, SMB, TLS, and Kerberos objects are created only when the source provides the required context. SMB file timestamps now use the documented seconds unit. Unrecognized HTTP methods retain their names, and SMTP normalization populates current email address fields while preserving the original envelope fields. Validation continues to report required actors, principals, and email messages that the sensor did not observe.
