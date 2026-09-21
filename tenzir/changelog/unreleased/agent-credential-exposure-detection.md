---
title: Agent credential exposure detection
type: feature
authors:
  - codex
prs:
  - 0
created: 2026-09-14T19:30:00.000000Z
---

The `tenzir` package now flags credential or secret material appearing in an
AI agent's prompt, completion, or tool argument as an OCSF Detection Finding.

```tql
subscribe "ocsf"
tenzir::detect::agent::credential_exposure
publish "findings"
```

The detector matches structural credential signatures only, such as an AWS
access key ID, a PEM private key header, or a GitHub or Slack token prefix,
never the surrounding language. The matched text never leaves the operator:
the finding carries the credential kind and a SHA-256 evidence hash, so
repeated leaks of the same secret correlate without exposing it downstream.

Lives in the `tenzir::detect::agent` namespace, alongside the network
detectors in `tenzir::detect::network`.
