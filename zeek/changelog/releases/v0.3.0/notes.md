This release makes Zeek SMTP records with a rejected or unfinished envelope valid OCSF Email Activity events with a status from the server's last reply, and maps TLS fingerprints and server names to the endpoints. HTTP Activity events gain proxy headers, X-Forwarded-For addresses, and complete URLs with the Host header port. Zeek events now keep the connection UID only in `metadata.correlation_uid`.

## 💥 Breaking changes

### Zeek connection UIDs only as correlation UIDs

Zeek events no longer set `metadata.original_event_uid`. OCSF defines this attribute as the identifier of the one raw log entry an event came from, but Zeek's `uid` identifies a connection, which many records across `conn.log`, `smtp.log`, `files.log`, and other logs share. Use `metadata.correlation_uid` instead, which holds the same value and exists to link related events. Network events also keep the connection UID in `connection_info.uid`.

Before:

```tql
where metadata.original_event_uid == "CmRFd61N7G7YA909D1"
```

After:

```tql
where metadata.correlation_uid == "CmRFd61N7G7YA909D1"
```

*By @zedoraps.*

### Zeek SMTP envelope addresses in Email Activity

Zeek SMTP records with an SMTP envelope but no message headers now produce valid OCSF Email Activity events. Zeek logs the header `From` and `To` addresses only once the client transmits the message, so transactions that ended earlier, most often because the server rejected the sender or a recipient, previously produced Email Activity events without the `from` or `to` address that the `email` object requires.

The `email.from` and `email.to` fields now take the header addresses and fall back to the envelope sender (`MAIL FROM`) and recipients (`RCPT TO`). The `email.from_mailbox`, `email.to_mailboxes`, and `email.cc_mailboxes` fields hold header values only, so an empty `from_mailbox` tells that `from` came from the envelope. For example, find rejected envelopes with:

```tql
where class_uid == 4009 and email.from_mailbox? == null and status_id == 2
```

The envelope itself moves from the deprecated `email.smtp_from` and `email.smtp_to` fields to `email.return_path` and `email.delivered_to_list`, which always hold the envelope sender and recipients. Zeek SMTP events no longer set `email.smtp_from` or `email.smtp_to`, so queries that read them need to switch to the new fields.

Email Activity events also leave two more deprecated attributes behind. The address from the `Reply-To` header moves from `email.reply_to` to the list `email.reply_to_list`, next to the unchanged `email.reply_to_mailboxes`. The HELO/EHLO argument, the host name that the client reports for itself, moves from `smtp_hello` to the class attribute `command`:

```tql
// Before
where smtp_hello == "localhost"
// After
where class_uid == 4009 and command == "localhost"
```

`command` holds only the argument, because Zeek doesn't log whether the client sent HELO or EHLO.

Records without an envelope or header addresses, such as an SMTP negotiation alone, become OCSF Network Activity with `app_protocol_name: "smtp"` and keep partial message details, such as `helo` and `subject`, under `unmapped`.

All SMTP records now take `status`, `status_code`, and `status_detail` from Zeek's `last_reply`. The class of the reply code decides: 2xx is a success, 4xx and 5xx a failure, and a 3xx reply such as `354` after `DATA` leaves the transaction unfinished, so its status is unknown. Both classes now map the hosts from Zeek's `path` that handed on the message before it reached the client to `src_endpoint.intermediate_ips`, instead of placing the whole path, including the connection's own server and client, in the `dst_endpoint.intermediate_ips` of Email Activity events.

Header lists distinguish known from unknown absence: when Zeek saw the message headers, a missing `To`, `Cc`, or `Reply-To` header yields an empty list, and without any headers, such as after a rejected envelope, these lists stay null.

*By @zedoraps.*

## 🔧 Changes

### Complete URLs for Zeek HTTP requests

HTTP Activity events now carry the complete URL of a request in `http_request.url.url_string`, with `url.scheme` set to `http`, since Zeek only parses cleartext HTTP. For a request target in origin form, such as `/index.html`, the URL combines the scheme, the Host header, and the target. A port in the Host header, such as `203.176.135.102:8082`, now maps to `url.port` and no longer appears in `url.hostname`. The URL never takes the port of the connection. A proxy request in absolute form, such as `http://azenv.net/`, keeps the URL as sent and takes the scheme, host, port, path, and query from it, so its `url.path` no longer holds the whole URL. A request without a Host header keeps its path and query string but has no URL string. CONNECT targets, such as `example.org:443`, and other request targets that name no URL map no `url` object and stay in `unmapped.uri`.

Zeek logs `uri` percent-decoded, so `url_string` holds the decoded form.

```tql
where http_request.url.port? == 8082
```

*By @zedoraps.*

### Zeek proxy headers as HTTP request headers

HTTP Activity events now map the proxy headers that Zeek logs in `proxied`, such as `X-FORWARDED-FOR`, `VIA`, and `FORWARDED`, to `http_request.http_headers`, after the headers from `client_headers`. A header that `client_headers` already lists with the same value does not repeat. The addresses in X-Forwarded-For map to `src_endpoint.intermediate_ips`, in header order, if every entry is an address. Clients control the header, so treat the addresses as claims. If an entry is no address, as in Log4Shell probes, no addresses map, but the header still does. `proxied` no longer appears in `unmapped`.

```tql
where 137.135.117.126 in src_endpoint.intermediate_ips?
```

*By @zedoraps.*

### Zeek TLS fingerprints and server names on endpoints

Zeek TLS records whose handshake never finished no longer produce an invalid OCSF `tls` object, and every TLS record now exposes its JA3 and JA3S fingerprints and its SNI on the endpoints. Zeek logs no TLS version when it saw no ServerHello, for example when the client sent only a ClientHello or the server answered only with an alert. These records previously carried a `tls` object without the `version` that OCSF requires. They now stay Network Activity events without a `tls` object, and facts without an OCSF counterpart, such as `ssl_history`, remain under `unmapped`.

For all TLS records, whether the handshake finished or not:

- `src_endpoint.fingerprints` holds the client's JA3 and `dst_endpoint.fingerprints` the server's JA3S, as fingerprints with `algorithm_id: 99` (Other) and `algorithm` set to `JA3` or `JA3S`.
- `dst_endpoint.hostname` holds the SNI when it names a host. An SNI that is an IP address, with or without a port, stays in `tls.sni`, or under `unmapped.server_name` when there is no `tls` object.
- `status_code` holds the numeric TLS alert code next to the alert name in `status_detail`.

Completed handshakes keep `tls.ja3_hash`, `tls.ja3s_hash`, and `tls.sni`. Failed handshakes often come from malware, so you can now hunt for a client fingerprint or a server name across all TLS records, for example:

```tql
where "37f463bf4616ecd445d4a1937da06e19" in src_endpoint.fingerprints?.map(x => x.value)
```

*By @zedoraps.*
