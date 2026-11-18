This release maps Suricata file, Kerberos, and SMTP events to the OCSF classes that their observed evidence supports, so they no longer require actors, users, or email header addresses that the sensor never saw.

## 🔧 Changes

### Network Activity for Kerberos without a client

Kerberos events without a client principal now map to Network Activity instead of Authentication, which requires the authenticated user. This affects TGS requests, whose client identity is encrypted, errors without a client name, and AS requests that omit one, such as scanner probes. The message type, service principal, realm, and failed request remain under `unmapped.krb5`, and errors keep their code in `status_code`. Kerberos events that name a client still map to Authentication.

*By @zedoraps.*

### Network Activity for SMTP without header addresses

SMTP events now map to Email Activity only when Suricata parsed a sender or recipient from the message headers, which Email Activity requires. Transactions with only an SMTP envelope, such as rejected, interrupted, or incompletely parsed messages, map to Network Activity traffic tagged with the SMTP application protocol. Their HELO name, envelope, and any partial message details remain under `unmapped`.

*By @zedoraps.*

### Protocol classes for Suricata file events

Suricata `fileinfo` events no longer map to the deprecated Network File Activity class, which requires an actor that a network sensor cannot observe. They now use the class of the protocol that transferred the file:

- HTTP transfers become HTTP Activity with the file in `file`, next to the request and response of the transaction.
- SMB transfers become SMB Activity with the file in `file`, including its share path, ID, and the SMB command.
- SMTP attachments become Email Activity with the file in `email.files` when the message has header addresses, and Network Activity otherwise.
- Files from other protocols become Network Activity traffic, with the file details under `unmapped.fileinfo`.

The file keeps its name, size, hashes, and libmagic description, and `metadata.log_name` still says `fileinfo`. Because Suricata logs files in their transfer direction, downloads used to name the server as source. The client is now `src_endpoint` whenever the standard ports, the HTTP Host header, the request method, or the SMB command identify the server. HTTP uploads without such evidence keep the direction that Suricata logged.

*By @zedoraps.*
