---
title: Defender detection evidence without resource prefixes
type: bugfix
authors:
  - zedoraps
created: 2026-11-18T10:40:12.897818Z
---

Microsoft Defender detections (1116/1117) now list each detected file on disk once in `evidences`, instead of one file holding the whole `Path` with its resource prefixes.

| Resource in `Path` | Evidence now |
|---|---|
| `file:_C:\x.exe`, `containerfile:_C:\x.zip` | The file |
| `file:_C:\x.zip->(Zip:y.exe)` | The container, `C:\x.zip` |
| `webfile:_C:\x.exe`, followed by URL and process | The local path, `C:\x.exe` |
| `regkey:_…` and other resources | None |

```tql
evidences: [
  {file: {path: "C:\\Users\\rchen\\Downloads\\tools.zip", name: "tools.zip", type_id: 1}},
  {file: {path: "C:\\Users\\rchen\\Downloads\\setup.exe", name: "setup.exe", type_id: 1}},
],
```

The complete list stays in `unmapped.EventData.Path`.
