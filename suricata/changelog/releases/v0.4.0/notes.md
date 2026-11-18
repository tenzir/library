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

### Network Activity for Kerberos without a client

Kerberos events without a client principal now map to Network Activity instead of Authentication, which requires the authenticated user. This affects TGS requests, whose client identity is encrypted, errors without a client name, and AS requests that omit one, such as scanner probes. The message type, service principal, realm, and failed request remain under `unmapped.krb5`, and errors keep their code in `status_code`. Kerberos events that name a client still map to Authentication.

*By @zedoraps.*

### Protocol classes for Suricata file events

Suricata `fileinfo` events no longer map to the deprecated Network File Activity class, which requires an actor that a network sensor cannot observe. They now use the class of the protocol that transferred the file:

- HTTP transfers become HTTP Activity with the file in `file`, next to the request and response of the transaction.
- SMB transfers become SMB Activity with the file in `file`, including its share path, ID, and the SMB command.
- SMTP attachments become Email Activity with the file in `email.files`.
- Files from other protocols become Network Activity traffic, with the file details under `unmapped.fileinfo`.

The file keeps its name, size, hashes, and libmagic description, and `metadata.log_name` still says `fileinfo`. Because Suricata logs files in their transfer direction, downloads used to name the server as source. The client is now `src_endpoint` whenever the standard ports, the HTTP Host header, the request method, or the SMB command identify the server. HTTP uploads without such evidence keep the direction that Suricata logged.

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
