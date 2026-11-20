---
title: Application crash fields as Windows writes them
type: bugfix
authors:
  - zedoraps
created: 2026-11-18T10:40:09.905177Z
---

Application crashes (1000) now map the values that Windows writes, with or without field names. The faulting process and module are filled in, including the module from `ModuleName` and `ModulePath`. The crashed process is also the actor, and the faulting module has an unknown load type. Hexadecimal process IDs and exception codes without letters keep their value.
