---
title: Windows event titles in message
type: change
authors:
  - zedoraps
prs:
  - 261
created: 2026-11-22T16:00:00.000000Z
---

The OCSF `message` of a Windows event is its title, such as `An account was successfully logged on`, instead of the full rendered message.

- The title is the first line of the rendered message without its closing period or colon. The full message stays in `unmapped.RenderingInfo.Message` when it says more.
- Logon, logoff, Kerberos, NTLM, and other authentication events without a rendered message, such as from Windows Event XML, get the title from Microsoft's event documentation.
- Rendered messages in Windows Event XML keep their line breaks.
