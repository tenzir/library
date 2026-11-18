---
title: Network Activity for SMTP without header addresses
type: change
authors:
  - zedoraps
created: 2026-11-18T10:12:11.500363Z
---

SMTP events now map to Email Activity only when Suricata parsed a sender or recipient from the message headers, which Email Activity requires. Transactions with only an SMTP envelope, such as rejected, interrupted, or incompletely parsed messages, map to Network Activity traffic tagged with the SMTP application protocol. Their HELO name, envelope, and any partial message details remain under `unmapped`.
