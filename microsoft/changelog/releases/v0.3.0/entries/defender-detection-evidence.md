---
title: Defender detection evidence
type: bugfix
authors:
  - zedoraps
created: 2026-11-18T10:40:12.897818Z
---

Microsoft Defender detections (1116/1117) now list each detected file on disk once in `evidences`, instead of one file holding the whole `Path` with its resource prefixes.

**Windows writes** (Microsoft Defender 1116):

```xml
<Provider Name="Microsoft-Windows-Windows Defender"/>  <EventID>1116</EventID>
<Data Name="Path">file:_C:\Users\rchen\Downloads\credtool.sys</Data>  <!-- resource type, then path -->
```

A detection with several resources lists them all in `Path`, separated by `; `, such as `containerfile:_C:\Users\rchen\Downloads\tools.zip; file:_C:\Users\rchen\Downloads\tools.zip->(Zip:credtool.exe); webfile:_C:\Users\rchen\Downloads\setup.exe|https://downloads.example.test/setup.exe|pid:4312,…`.

**OCSF before → now:**

| Resource in `Path` | Before | Now |
|---|---|---|
| `file:_C:\x.exe`, `containerfile:_C:\x.zip` | One file with the whole `Path` as its path, prefix included | The file |
| `file:_C:\x.zip->(Zip:y.exe)` | Part of that one file | The container, `C:\x.zip` |
| `webfile:_C:\x.exe`, followed by URL and process | Part of that one file | The local path, `C:\x.exe` |
| `regkey:_…` and other resources | A file named after the last path element, such as `Run` | None |

```tql
evidences: [
  {file: {path: "C:\\Users\\rchen\\Downloads\\tools.zip", name: "tools.zip", type_id: 1}},
  {file: {path: "C:\\Users\\rchen\\Downloads\\setup.exe", name: "setup.exe", type_id: 1}},
],
```

The complete list stays in `unmapped.EventData.Path`.

**Why:** Defender writes every detected resource into one `Path`, each with a type prefix, and only some of them are files on disk. A file evidence needs the path of such a file, so the mapping splits the list, strips the prefixes, and skips the other resources.
