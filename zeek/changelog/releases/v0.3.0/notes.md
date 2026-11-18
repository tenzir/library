This release maps Zeek SMTP records without message header addresses, such as rejected envelopes, to OCSF Network Activity instead of incomplete Email Activity events. All SMTP records now carry a status from the server's last reply.

## 🔧 Changes

### Zeek SMTP envelopes without message headers as network activity

Zeek SMTP records without message headers now become OCSF Network Activity instead of Email Activity. OCSF identifies an email by its header `From` and `To` addresses, which Zeek logs only once the client transmits the message. Transactions that ended earlier, most often because the server rejected the sender or a recipient, previously produced Email Activity events without a valid `email` object.

These records now report SMTP traffic with `app_protocol_name: "smtp"` and keep the SMTP envelope and any partial message details, such as `mailfrom`, `rcptto`, `helo`, and `subject`, under `unmapped`. For example, find rejected SMTP transactions with:

```tql
where class_uid == 4001 and app_protocol_name? == "smtp" and status_id == 2
```

All SMTP records now take `status`, `status_code`, and `status_detail` from Zeek's `last_reply`, including records of an SMTP negotiation without an envelope. The class of the reply code decides: 2xx is a success, 4xx and 5xx a failure, and a 3xx reply such as `354` after `DATA` leaves the transaction unfinished, so its status is unknown. Records with header addresses remain Email Activity events. Both classes now map the hosts from Zeek's `path` that handed on the message before it reached the client to `src_endpoint.intermediate_ips`, instead of placing the whole path, including the connection's own server and client, in the `dst_endpoint.intermediate_ips` of Email Activity events.

*By @zedoraps.*
