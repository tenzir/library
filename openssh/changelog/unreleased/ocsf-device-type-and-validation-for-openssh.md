---
title: Required OCSF device type for OpenSSH
type: bugfix
created: 2026-11-04T13:58:44.845909Z
---

OpenSSH normalization now sets the required OCSF device type to Unknown when a host is present and its type is not reported. Host records therefore satisfy the OCSF device-type requirement without guessing whether the host is a server or another device type.
