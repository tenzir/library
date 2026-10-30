---
title: Preserved Windows and Graph activity classification
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:35.011614Z
prs:
  - 208
---

Windows and Microsoft Graph mappings now preserve known OCSF classes and activities when required context is missing. Validation reports incomplete actor, process, file, script, or peripheral context as warnings. Windows-specific attributes declare the Windows extension.

Optional identities are built from reported source identifiers. Unused executable paths, user display names, and other context retain their source fields in `unmapped`; they are not promoted into unidentified OCSF objects.
