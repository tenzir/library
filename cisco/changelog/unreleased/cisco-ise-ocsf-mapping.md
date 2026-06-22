---
title: Cisco ISE syslog parsing and OCSF mapping
type: feature
authors:
  - zedoraps
  - claude
created: 2026-06-18T00:00:00Z
---

The `cisco` package now ingests Cisco Identity Services Engine (ISE) syslog.
Point `read_syslog` (or `parse_syslog`) at the ISE remote-target stream and pipe
it into the new operators.

- `cisco::ise::parse` parses an ISE message body—header, message code, severity,
  and the comma-separated attribute value pairs—into a normalized `cisco.ise.*`
  event. It reads the `CISE_<Category>` tag from the start of the body, where
  `read_syslog` leaves it for the ISE remote-target format, and classifies the
  event from it, falling back to the message code. The body and category fields
  are configurable (`message=...`, `category=...`). Attribute values are kept
  verbatim so identifiers such as MAC addresses and session IDs are not
  corrupted by type inference.
- `cisco::ise::reassemble` reassembles messages that ISE splits into numbered
  segments sharing a message id. It windows segments by message id on an
  event-time field, concatenates their payloads in segment order, and preserves
  the `CISE_<Category>` tag so the parser can recover the category. Because BSD
  syslog timestamps carry no year, the multi-segment example shows how to assign
  the current year (with year-boundary rollover) before windowing. Fragments
  whose header segment never arrives are kept rather than dropped: the parser
  tags them `cisco.ise.incomplete` and the mapper labels them
  (`metadata.labels`) as an OCSF Base Event, preserving their attributes.

The `cisco::ise::ocsf::map` operator maps Passed Authentications and Failed
Attempts to OCSF Authentication (3002) logon attempts. RADIUS Accounting maps to
OCSF Network Activity (4001)—Start opens the connection, Stop closes it, and an
Interim-Update is a traffic report—carrying the session's byte and packet
counters, duration, user, device, and endpoints. All other ISE categories are
routed to OCSF Base Events.
