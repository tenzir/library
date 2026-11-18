---
title: Protocol classes for Suricata file events
type: change
authors:
  - zedoraps
created: 2026-11-18T10:12:09.945444Z
---

Suricata `fileinfo` events no longer map to the deprecated Network File Activity class, which requires an actor that a network sensor cannot observe. They now use the class of the protocol that transferred the file:

- HTTP transfers become HTTP Activity with the file in `file`, next to the request and response of the transaction.
- SMB transfers become SMB Activity with the file in `file`, including its share path, ID, and the SMB command.
- SMTP attachments become Email Activity with the file in `email.files` when the message has header addresses, and Network Activity otherwise.
- Files from other protocols become Network Activity traffic, with the file details under `unmapped.fileinfo`.

The file keeps its name, size, hashes, and libmagic description, and `metadata.log_name` still says `fileinfo`. Because Suricata logs files in their transfer direction, downloads used to name the server as source. The client is now `src_endpoint` whenever the standard ports, the HTTP Host header, the request method, or the SMB command identify the server. HTTP uploads without such evidence keep the direction that Suricata logged.
