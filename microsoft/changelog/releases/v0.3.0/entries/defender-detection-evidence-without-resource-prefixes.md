---
title: Defender detection evidence without resource prefixes
type: bugfix
authors:
  - zedoraps
created: 2026-11-18T10:40:12.897818Z
---

Microsoft Defender detections (1116/1117) now list each detected file on disk once in `evidences`, without the resource prefix that Defender writes in `Path`, such as `file:_`:

- Container files (`containerfile:_`) and downloads (`webfile:_`) count as files. For a download, the evidence is the local path, without the URL and the process details.
- An archive member, such as `file:_C:\x.zip->(Zip:y.exe)`, becomes its container, `C:\x.zip`, because OCSF has no field for archive members.
- Other resources, such as registry keys, aren't evidence. A detection without a file has no `evidences`.

The complete list stays in `unmapped.EventData.Path`.
