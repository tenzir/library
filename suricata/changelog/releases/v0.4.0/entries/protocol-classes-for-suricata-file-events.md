---
title: Protocol classes for Suricata file events
type: change
authors:
  - zedoraps
created: 2026-11-18T10:12:09.945444Z
---

Suricata `fileinfo` events no longer map to the deprecated Network File Activity class, which requires an actor that a network sensor cannot observe. They now use the class of the protocol that transferred the file:

- HTTP transfers become HTTP Activity with the file in `file`, next to the request and response of the transaction, when Suricata knows the name of the file.
- SMB transfers become SMB Activity with the file in `file`, including its share path, ID, and the SMB command.
- SMTP attachments become Email Activity with the file in `email.files`.
- Files from other protocols become Network Activity traffic, with the file details under `unmapped.fileinfo`.

The file keeps its name, size, hashes, and libmagic description, and `metadata.log_name` still says `fileinfo`. When Suricata computed no hashes, `file.hashes` is null instead of an empty list.

For HTTP, Suricata names a file only after the `Content-Disposition` filename of a response or the filename of a multipart upload, such as `aehgwjwgij.zip`. Otherwise, it falls back to the URL path, which `http_request.url.path` already holds and which always begins with `/`. Such events no longer report the path as `file.name`, and have no `file`. The file size becomes `http_response.body_length` when the evidence below identifies a response body, and `http_request.body_length` for a request body. A response body length that Suricata logged for the transaction takes precedence. Otherwise, the size stays in `unmapped.fileinfo.size`, next to the path in `unmapped.fileinfo.filename` and any hashes. A server that sends a name beginning with `/`, such as `filename="/etc/passwd"`, is treated the same way.

Suricata logs a file event in the direction of the file, not of the connection, so downloads used to name the server as source. The client is now `src_endpoint` whenever hard evidence identifies the direction:

- For HTTP, the ports 80, 8080, and 443, a Host header with the address of one side, or a Host header with the port of one side name the server. A response with a zero-length body makes the file the request body, and a content range or file offsets make it the response body. The request method is no evidence, because a GET request may carry a body.
- For SMB, the ports 139 and 445 and the read or write command name the server.

When an HTTP file event has no such evidence, or the evidence contradicts itself, it names no `src_endpoint` and `dst_endpoint`. It stays HTTP Activity with its `connection_info`, and keeps the observed `src_ip`, `src_port`, `dest_ip`, and `dest_port` in `unmapped`.
