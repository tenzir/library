---
title: Refactor package to use UDOs
type: breaking
author: mavam
created: 2025-12-12T11:03:57.956803Z
---

Refactor the package to use modular user-defined operators (UDOs) instead of individual pipelines per OCSF event class. The package ID changed from `amazon-security-lake` to `amazon_security_lake`.

The new UDOs are:

- `amazon_security_lake::cast`: casts OCSF events for Security Lake compatibility
- `amazon_security_lake::send`: sends OCSF events to Security Lake using the event's `class_uid` for dynamic routing

This replaces ~50 nearly identical pipelines with a single `send-all` pipeline that handles all OCSF event classes dynamically.
