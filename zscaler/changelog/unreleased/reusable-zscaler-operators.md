---
title: Reusable Zscaler operators
type: breaking
authors:
- mavam
prs:
  - 147
created: 2025-11-02
---

Zscaler parsing and OCSF mapping are now available as reusable operators.

Use the package operators directly in your own ZIA NSS workflows instead of
depending on a fixed packaged pipeline:

```tql
zscaler::ocsf::map
```

This gives you control over where logs come from, how they are routed, and when
they are mapped to OCSF.
