This release maps Suricata file, Kerberos, and SMTP events to the OCSF classes that their observed evidence supports, so they no longer require actors or users that the sensor never saw. SMTP events without parsed message headers become valid Email Activity events whose sender and recipients come from the SMTP envelope.

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

### SMTP envelope addresses in Email Activity

SMTP events with an SMTP envelope but no parsed message headers now produce valid OCSF Email Activity events. Suricata logs the header `From` and `To` addresses only when its MIME parser found them, so rejected, interrupted, or incompletely parsed messages previously produced Email Activity events without the `from` or `to` address that the `email` object requires.

The `email.from` and `email.to` fields now take the header addresses and fall back to the envelope sender (`MAIL FROM`) and recipients (`RCPT TO`). The `email.from_mailbox`, `email.to_mailboxes`, and `email.cc_mailboxes` fields hold header values only, so an empty `from_mailbox` tells that `from` came from the envelope. For example, find messages without a parsed header sender with:

```tql
where class_uid == 4009 and email.from_mailbox? == null
```

The envelope itself moves from the deprecated `email.smtp_from` and `email.smtp_to` fields to `email.return_path` and `email.delivered_to_list`, which always hold the envelope sender and recipients. Suricata SMTP and `fileinfo` events no longer set `email.smtp_from` or `email.smtp_to`, so queries that read them need to switch to the new fields.

Plain HELO and STARTTLS sessions without an envelope or header addresses map to Network Activity traffic tagged with the SMTP application protocol, with their HELO name under `unmapped`.

*By @zedoraps.*
