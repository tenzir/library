This release maps Suricata file, Kerberos, and SMTP events to the OCSF classes that their observed evidence supports, so they no longer require actors or users that the sensor never saw. SMTP events without parsed message headers become valid Email Activity events whose sender and recipients come from the SMTP envelope, SMTP events replace the deprecated `smtp_from`, `smtp_to`, and `smtp_hello` attributes with their successors, and they no longer report an unknown status. TLS events now expose their JA3 and JA3S fingerprints and server name on the endpoints. Suricata events no longer set `metadata.original_event_uid`; the flow ID remains in `metadata.correlation_uid`.

## 💥 Breaking changes

### SMTP envelope addresses in Email Activity

SMTP events with an SMTP envelope but no parsed message headers now produce valid OCSF Email Activity events. Suricata logs the header `From` and `To` addresses only when its MIME parser found them, so rejected, interrupted, or incompletely parsed messages previously produced Email Activity events without the `from` or `to` address that the `email` object requires.

The `email.from` and `email.to` fields now take the header addresses and fall back to the envelope sender (`MAIL FROM`) and recipients (`RCPT TO`). The `email.from_mailbox`, `email.to_mailboxes`, and `email.cc_mailboxes` fields hold header values only, so an empty `from_mailbox` tells that `from` came from the envelope. For example, find messages without a parsed header sender with:

```tql
where class_uid == 4009 and email.from_mailbox? == null
```

The envelope itself moves from the deprecated `email.smtp_from` and `email.smtp_to` fields to `email.return_path` and `email.delivered_to_list`, which always hold the envelope sender and recipients. Suricata SMTP and `fileinfo` events no longer set `email.smtp_from` or `email.smtp_to`, so queries that read them need to switch to the new fields.

Email Activity events also move the HELO/EHLO argument, the host name that the client reports for itself, from the deprecated `smtp_hello` to the class attribute `command`:

```tql
// Before
where smtp_hello == "localhost"
// After
where class_uid == 4009 and command == "localhost"
```

`command` holds only the argument, because Suricata doesn't log whether the client sent HELO or EHLO.

Plain HELO and STARTTLS sessions without an envelope or header addresses map to Network Activity traffic tagged with the SMTP application protocol, with their HELO name under `unmapped`, because Network Activity has no `command` attribute.

Suricata logs no SMTP reply codes, so SMTP Email Activity and Network Activity events no longer set `status` and `status_id`, instead of reporting an `Unknown` status that told nothing. Queries such as `status_id == 0` no longer match these events.

*By @zedoraps.*

### Suricata flow IDs only as correlation UIDs

Suricata events no longer set `metadata.original_event_uid`. OCSF defines this attribute as the identifier of the one raw log entry an event came from, but Suricata's `flow_id` identifies a flow, which the `flow`, `alert`, `http`, `fileinfo`, and other events of that flow share. Use `metadata.correlation_uid` instead, which holds the same value and exists to link related events. Network events also keep the flow ID in `connection_info.uid`.

Before:

```tql
where metadata.original_event_uid == "1349859816939076"
```

After:

```tql
where metadata.correlation_uid == "1349859816939076"
```

*By @zedoraps.*

## 🔧 Changes

### Decoded MIME attachment names

Email Activity events from Suricata SMTP and `fileinfo` events now decode attachment names that the message encodes as a single Base64-encoded UTF-8 word (RFC 2047). For example, `email.files[].name` holds `66787196844.zip` instead of `=?UTF-8?B?NjY3ODcxOTY4NDQuemlw?=`. Names in other encodings or charsets, such as `=?UTF-8?Q?…?=` or `=?ISO-8859-1?B?…?=`, and names that consist of several encoded words stay as Suricata logged them.

*By @zedoraps.*

### Host header ports in HTTP URLs

HTTP, file, and alert events now map the port that the client wrote in the Host header, Suricata's `http.http_port`, to `http_request.url.port`, and include it in `http_request.url.url_string`. For example, a request with `Host: 203.176.135.102:8082` has the URL `http://203.176.135.102:8082/ono32/…` instead of `http://203.176.135.102/ono32/…`. Without a port in the Host header, the URL has no port, even when the connection uses a non-standard one. Suricata logs port 0 for requests without a host, which stays in `unmapped.http.http_port`.

*By @zedoraps.*

### Network Activity for Kerberos without a client

Kerberos events without a client principal now map to Network Activity instead of Authentication, which requires the authenticated user. This affects TGS requests, whose client identity is encrypted, errors without a client name, and AS requests that omit one, such as scanner probes. The message type, service principal, realm, and failed request remain under `unmapped.krb5`, and errors keep their code in `status_code`. Kerberos events that name a client still map to Authentication.

A `KDC_ERR_PREAUTH_REQUIRED` error, which the KDC sends at the start of every regular logon, keeps its Failure status but now has Informational instead of Low severity.

*By @zedoraps.*

### Protocol classes for Suricata file events

Suricata `fileinfo` events no longer map to the deprecated Network File Activity class, which requires an actor that a network sensor cannot observe. They now use the class of the protocol that transferred the file:

- HTTP transfers become HTTP Activity with the file in `file`, next to the request and response of the transaction, when Suricata knows the name of the file.
- SMB transfers become SMB Activity with the file in `file`, including its share path, ID, and the SMB command. SMB Activity defines activities only for the dispositions of a create request, so reads and writes have `activity_id` 99 (Other) with the `activity_name` `Read` or `Write`.
- SMTP attachments become Email Activity with the file in `email.files`.
- Files from other protocols become Network Activity traffic, with the file details under `unmapped.fileinfo`.

The file keeps its name, size, hashes, and libmagic description, and `metadata.log_name` still says `fileinfo`. When Suricata computed no hashes, `file.hashes` is null instead of an empty list.

For HTTP, Suricata names a file only after the `Content-Disposition` filename of a response or the filename of a multipart upload, such as `aehgwjwgij.zip`. Otherwise, it falls back to the URL path, which `http_request.url.path` already holds and which always begins with `/`. Such events no longer report the path as `file.name`, and have no `file`. The file size becomes `http_response.body_length` when the evidence below identifies a response body, and `http_request.body_length` for a request body. A response body length that Suricata logged for the transaction takes precedence. Otherwise, the size stays in `unmapped.fileinfo.size`, next to the path in `unmapped.fileinfo.filename` and any hashes. A server that sends a name beginning with `/`, such as `filename="/etc/passwd"`, is treated the same way.

Suricata logs a file event in the direction of the file, not of the connection, so downloads used to name the server as source. The client is now `src_endpoint` whenever hard evidence identifies the direction:

- For HTTP, the ports 80, 8080, and 443, a Host header with the address of one side, or a Host header with the port of one side name the server. A response with a zero-length body makes the file the request body, and a content range or file offsets make it the response body. The request method is no evidence, because a GET request may carry a body.
- For SMB, the ports 139 and 445 and the read or write command name the server.

When an HTTP or SMB file event has no such evidence, or the evidence contradicts itself, it names no `src_endpoint` and `dst_endpoint`. It keeps its class and `connection_info`, and keeps the observed `src_ip`, `src_port`, `dest_ip`, and `dest_port` in `unmapped`. Such SMB events lack the endpoint that SMB Activity requires, so `ocsf_cast` warns about them.

*By @zedoraps.*

### TLS fingerprints and server names on Suricata endpoints

Suricata TLS events now expose the JA3 and JA3S fingerprints and the server name on the endpoints, so you can hunt for them like any other endpoint attribute:

- `src_endpoint.fingerprints` holds the client's JA3 and `dst_endpoint.fingerprints` the server's JA3S, as fingerprints with `algorithm_id: 99` (Other) and `algorithm` set to `JA3` or `JA3S`.
- `dst_endpoint.hostname` holds the SNI when it names a host. An SNI that is an IP address, with or without a port, stays in `tls.sni` only.

The `tls.ja3_hash`, `tls.ja3s_hash`, and `tls.sni` fields stay as before. For example, find all connections of a client fingerprint with:

```tql
where "37f463bf4616ecd445d4a1937da06e19" in src_endpoint.fingerprints?.map(x => x.value)
```

TLS events for which Suricata logged the version `UNDETERMINED`, which happens when it saw no negotiated version, such as for a lone ClientHello, no longer carry a `tls` object, because OCSF models a negotiated session there. They stay Network Activity events with the server name in `dst_endpoint.hostname`, and the version remains under `unmapped.tls.version`.

*By @zedoraps.*

### X-Forwarded-For addresses as intermediate IPs

HTTP, file, and alert events now map the addresses in the X-Forwarded-For header to `src_endpoint.intermediate_ips`, in header order. The addresses come from `http.xff`, the raw header, or from `xff`, the address that Suricata's `xff` setting picks in `extra-data` mode. Detection Findings carry them in the source endpoint of their evidence. Mapped addresses no longer appear in `unmapped`. Clients control the header, so treat the addresses as claims. If an entry is no address, such as `unknown`, the other entries still map, and the raw header also stays in `unmapped.http.xff`. File events whose direction is unknown have no client endpoint and keep both fields in `unmapped`.

The mappings also drop the records that they leave without values, such as `unmapped.http: {}` and `unmapped.smtp: {}`, and omit `unmapped` when nothing remains.

*By @zedoraps.*
